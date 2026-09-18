"""Deterministic document control for reviewed discovery publication.

Unknown historical versions are never inferred. Existing frontmatter remains
authoritative; only the version and update date are advanced automatically.
"""
import datetime as dt
import json
import re

from article_catalog import has_key, scalar

SEMVER = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')


def version_after(frontmatter, bump='minor'):
    if bump not in ('major', 'minor', 'patch'):
        raise ValueError('Document version change must be major, minor or patch')
    if not has_key(frontmatter, 'version'):
        return '1.0.0'
    version = scalar(frontmatter, 'version')
    if not SEMVER.fullmatch(version):
        raise ValueError('Existing document version must be stable MAJOR.MINOR.PATCH; correct it explicitly')
    major, minor, patch = map(int, version.split('.'))
    return {'major': f'{major+1}.0.0', 'minor': f'{major}.{minor+1}.0',
            'patch': f'{major}.{minor}.{patch+1}'}[bump]


def set_field(frontmatter, key, value):
    # Replace a complete YAML field, including any indented continuation.
    pattern = r'^' + re.escape(key) + r':[^\n]*(?:\n[ \t]+[^\n]*)*'
    frontmatter = re.sub(pattern, '', frontmatter, flags=re.M).strip('\n')
    return frontmatter + ('\n' if frontmatter else '') + key + ': ' + json.dumps(value, ensure_ascii=False)


def controlled(frontmatter, *, identifier, title, kind, date, owner, version, existing=False):
    keys = re.findall(r'^([A-Za-z_][\w-]*):', frontmatter, re.M)
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate document frontmatter keys')
    defaults = {'title': title, 'doc_type': kind, 'created': 'unknown' if existing else date,
                'owner': owner, 'steward': 'Transpara Knowledge Hub', 'author': 'Transpara Knowledge Hub',
                'project': 'wiki', 'repo': 'transpara-ai/wiki',
                'supersedes': [], 'canonical': kind == 'article'}
    if not has_key(frontmatter, 'doc_id') and not has_key(frontmatter, 'document_id'):
        defaults['doc_id'] = identifier
    if existing and not has_key(frontmatter, 'version'):
        defaults['version_history'] = 'Prior document versions unknown; first controlled baseline'
    for key, value in defaults.items():
        if not has_key(frontmatter, key):
            frontmatter = set_field(frontmatter, key, value)
    frontmatter = set_field(frontmatter, 'version', version)
    return set_field(frontmatter, 'updated', date)


def utc_date(timestamp):
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).date().isoformat()
