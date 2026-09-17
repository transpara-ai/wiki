"""Authenticated, space-scoped question answering over the published corpus."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import subprocess
import time

from ask_common import AskError, MAX_ARTICLES, MAX_CONTEXT, MAX_WIRE, DEADLINE_SECONDS, validate_result, resolve_effort

_lock = threading.Lock()
_readers = set()
_providers = set()


@contextmanager
def admission(reader, provider):
    with _lock:
        if reader in _readers or provider in _providers:
            raise AskError('A question is already running for you or this provider. Try again shortly.', 429)
        _readers.add(reader)
        _providers.add(provider)
    handles = []
    try:
        # All wiki processes/containers on Velia share the checkout volume.
        # Hold both reservations across selection AND answering; the private
        # dispatcher additionally serializes individual native CLI calls.
        directory = Path(__file__).resolve().parent.parent / '.private/ask-locks'
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        for identity in ('reader:' + reader, 'provider:' + provider):
            name = hashlib.sha256(identity.encode()).hexdigest() + '.lock'
            handle = (directory / name).open('a')
            handles.append(handle)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise AskError('A question is already running for you or this provider. Try again shortly.', 429) from None
        yield
    finally:
        for handle in reversed(handles):
            handle.close()
        with _lock:
            _readers.discard(reader)
            _providers.discard(provider)


def service(path, payload=None, timeout=5):
    host = os.environ.get('KNOWLEDGE_HUB_LLM_SSH_HOST', '')
    if not host:
        raise AskError('Wiki answers are not configured yet. Search is still available.')
    if not re.fullmatch(r'[a-zA-Z0-9_.:-]+', host):
        raise AskError('The shared provider connection is misconfigured.')
    args = ['ssh', '-T', '-F', '/dev/null', '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
            '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=5',
            '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2',
            '-o', 'ControlMaster=no', '-o', 'ControlPath=none',
            '-o', 'UserKnownHostsFile=/run/secrets/wiki-llm-known-hosts',
            '-i', '/run/secrets/wiki-llm-ssh-key', '-l', 'transpara', host]
    data = json.dumps({'operation': path.removeprefix('/'), 'payload': payload}).encode()
    # The key has a forced, root-owned JSON dispatcher on the Velia host; no caller
    # command, forwarding, PTY, or arbitrary provider flags are accepted.
    try:
        result = subprocess.run(args, input=data, capture_output=True, timeout=timeout + 8,
                                env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'})
        if result.returncode or len(result.stdout) > MAX_WIRE:
            raise ValueError()
        envelope = json.loads(result.stdout)
        if envelope['status'] != 200:
            raise AskError(envelope.get('error', 'The shared provider is unavailable.'), envelope['status'])
        return envelope['result']
    except subprocess.TimeoutExpired:
        raise AskError('The question timed out. Please retry.', 504) from None
    except (OSError, ValueError, KeyError):
        raise AskError('The shared provider connection is unavailable. Search is still available.') from None


def models():
    return service('/models')


def answer(payload, reader, dist):
    started = time.monotonic()
    fields = {'question', 'space', 'provider', 'model'}
    if not isinstance(payload, dict) or set(payload) not in (fields, fields | {'effort'}):
        raise AskError('Provide question, space, provider, model, and optional effort.', 400)
    if not all(isinstance(v, str) for v in payload.values()):
        raise AskError('Question and selections must be text.', 400)
    question = payload['question'].strip()
    if not 2 <= len(question) <= 4000:
        raise AskError('Enter a question between 2 and 4,000 characters.', 400)
    available = models()
    provider, model, space = (payload[k] for k in ('provider', 'model', 'space'))
    selected_model = next((m for m in available['models']
                           if m['provider'] == provider and m['id'] == model and m['enabled']), None)
    if selected_model is None:
        raise AskError('This model is not enabled on wiki. Select an available model.', 503)
    effort = resolve_effort(selected_model, payload.get('effort'))
    payload = {**payload, 'effort': effort}
    with admission(reader, provider):
        try:
            corpus = json.loads((Path(dist) / 'ask-index.json').read_text())
        except (OSError, ValueError):
            raise AskError('The question index is unavailable. Rebuild the wiki first.') from None
        if space != 'all' and space not in corpus['spaces']:
            raise AskError('Unknown or unpublished space.', 400)
        records = {a['id']: a for a in corpus['articles']
                   if space == 'all' or space in a['spaces']}
        revision = corpus['revision']
        if not records:
            return {'answer': 'There are no published articles in this space.', 'paragraphs': [],
                    'citations': [], 'insufficient_evidence': True,
                    'provider': provider, 'model': model, 'effort': effort, 'corpus_revision': revision}

        def complete(stage, context):
            remaining = DEADLINE_SECONDS - (time.monotonic() - started)
            if remaining <= 1:
                raise AskError('The question timed out. Please retry.', 504)
            result = service('/complete', {**payload, 'question': question, 'stage': stage,
                                          'context': context, 'timeout': remaining}, timeout=remaining)
            return validate_result(stage, result)

        catalog = [{'id': a['id'], 'title': a['title'],
                    'description': a['description']} for a in records.values()]
        selected = complete('select', catalog)['article_ids']
        if any(slug not in records for slug in selected):
            raise AskError('The model selected an article outside the published scope. Please retry.', 502)
        chosen = [records[slug] for slug in selected]
        if sum(len(a['text']) for a in chosen) > MAX_CONTEXT:
            raise AskError('The selected articles exceed the answer context limit. Narrow your question or space.', 422)
        if not chosen:
            return {'answer': 'The published articles do not provide enough evidence to answer this question.',
                    'paragraphs': [], 'citations': [], 'insufficient_evidence': True,
                    'provider': provider, 'model': model, 'effort': effort, 'corpus_revision': revision}
        result = complete('answer', [{'id': a['id'], 'title': a['title'], 'text': a['text']} for a in chosen])
        cited = []
        for paragraph in result['paragraphs']:
            ids = paragraph['article_ids']
            if any(slug not in selected for slug in ids):
                raise AskError('The model returned a citation outside its evidence. Please retry.', 502)
            if not ids and not result['insufficient_evidence']:
                raise AskError('The model returned an answer without supporting citations. Please retry.', 502)
            cited.extend(slug for slug in ids if slug not in cited)
        return {**result, 'answer': '\n\n'.join(p['text'] for p in result['paragraphs']),
                'citations': [{'id': slug, 'title': records[slug]['title'],
                               'href': records[slug]['href']} for slug in cited],
                'provider': provider, 'model': model, 'effort': effort, 'corpus_revision': revision}


def build_index(articles, spaces):
    """Input is already filtered by the renderer's publication/retirement gates."""
    for article in articles:
        headings = re.findall(r'^#{1,6}\s+(.+)$', article['text'], re.M)
        article['description'] = article['text'][:1400] + '\nHeadings: ' + '; '.join(headings)[:1800]
    serial = json.dumps({'spaces': spaces, 'articles': articles}, sort_keys=True, ensure_ascii=False)
    return {'revision': hashlib.sha256(serial.encode()).hexdigest(),
            'spaces': spaces, 'articles': articles}
