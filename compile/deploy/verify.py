#!/usr/bin/env python3
"""Smoke-test a local or private HTTPS deployment without creating corpus fixtures."""
import argparse
import hashlib
import http.client
import json
from pathlib import Path
from urllib.parse import urlsplit


def request(base, path, method='GET', token=None, host=None):
    url = urlsplit(base)
    if url.scheme not in ('http', 'https') or url.username or url.password or url.path not in ('', '/'):
        raise ValueError('Use a plain HTTP(S) origin URL')
    client_type = http.client.HTTPSConnection if url.scheme == 'https' else http.client.HTTPConnection
    client = client_type(url.hostname, url.port, timeout=300)
    headers = {}
    if token:
        headers['X-CivWiki-Authoring-Token'] = token
    if host:
        headers['Host'] = host
    try:
        client.request(method, path, headers=headers)
        response = client.getresponse()
        return response.status, response.read()
    finally:
        client.close()


def verify(base, manifest, *, token=None, host=None):
    def get(path):
        status, data = request(base, path, host=host)
        if status != 200:
            raise RuntimeError('%s returned HTTP %d' % (path, status))
        return data
    if json.loads(get('/api/health')) != {'ok': True}:
        raise RuntimeError('Unexpected health response')
    if json.loads(get('/version.json')) != {'version': manifest['version']}:
        raise RuntimeError('Deployed version differs from the snapshot')
    spaces = json.loads(get('/api/spaces'))['spaces']
    if {s['key'] for s in spaces} != {'civilization', 'platform', 'competition', 'devops'}:
        raise RuntimeError('The four expected spaces are not available')
    for route in ('/', '/repos.html', '/sources.html', '/ingest.html'):
        get(route)
    for space in spaces:
        get('/%s/index.html' % space['key'])
        for page in ('repos.html', 'sources.html', 'ingest.html'):
            get('/%s?space=%s' % (page, space['key']))
    articles = json.loads(get('/api/articles'))['articles']
    if {a['slug'] for a in articles} != set(manifest['active_article_slugs']):
        raise RuntimeError('The active article inventory differs from the snapshot')
    for article in articles:
        get('/' + article['slug'] + '.html')
    for ref in manifest['external_source_refs']:
        get('/source/' + hashlib.sha1(ref.encode()).hexdigest()[:16] + '.html')
    if request(base, '/api/rebuild', 'POST', host=host)[0] != 401:
        raise RuntimeError('Unauthenticated rebuild must be rejected')
    if token:
        status, body = request(base, '/api/rebuild', 'POST', token=token, host=host)
        if status != 200 or not json.loads(body).get('refresh', {}).get('ok'):
            raise RuntimeError('Authenticated rebuild failed')
        get('/api/health')
    return {'ok': True, 'version': manifest['version'], 'spaces': len(spaces),
            'articles': len(articles), 'external_sources': len(manifest['external_source_refs']),
            'authenticated_rebuild': bool(token)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.url, json.loads(args.manifest.read_text())), indent=2))
