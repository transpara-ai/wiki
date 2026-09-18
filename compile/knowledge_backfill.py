#!/usr/bin/env python3
"""Additively retain existing article-referenced evidence; never infer review status."""
import argparse
from pathlib import Path
from article_catalog import load_catalog
from knowledge_store import Store
from ingest_ops import OpRefused
from knowledge_sources import extract


def backfill(root,store):
    counts={'retained':0,'unchanged':0,'unsupported_or_refused':0,'missing':0}
    for article in load_catalog(root=root):
        for ref in article.raw_documents:
            path=(root/ref).resolve()
            if not path.is_relative_to((root/'raw').resolve()) or not path.is_file():
                counts['missing']+=1; continue
            try:
                raw=path.read_bytes()
                text,status=extract(raw,'text/plain')
                _,changed=store.capture('repository:'+ref,raw,text,{'path':ref,'space':article.primary_space,'classification':'internal','historical_article_classification':article.classification,
                    'historical_review':'unknown','extraction':status},'historical:'+article.slug)
                counts['retained' if changed else 'unchanged']+=1
            except (ValueError,OSError,OpRefused):
                # Refusals are counted without printing potentially sensitive source names or text.
                counts['unsupported_or_refused']+=1
    return counts


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    print(__import__('json').dumps(backfill(root,Store(root))))


if __name__=='__main__': main()
