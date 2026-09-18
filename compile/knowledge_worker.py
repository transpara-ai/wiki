#!/usr/bin/env python3
"""Independent discovery scheduler. Installation/enrollment is explicitly opt-in."""
import argparse
import fcntl
import os
from pathlib import Path
import signal
import time

from knowledge_store import Store, identity
from knowledge_workflow import Workflow
from knowledge_sources import Deferred

ROOT=Path(__file__).resolve().parents[1]


def schedule(store):
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        for row in db.execute("SELECT id FROM objects WHERE kind='monitor'").fetchall():
            m=store.get('monitor',row[0],db)
            if m['state']!='enabled' or (m.get('next_check') or 0)>time.time(): continue
            pending=db.execute("SELECT 1 FROM jobs WHERE kind='scan' AND state IN ('queued','running') AND json_extract(payload,'$.id')=?",(m['id'],)).fetchone()
            if not pending:
                store.enqueue('scan',identity('scan'),{'id':m['id']},60,db)
            m['next_check']=time.time()+m['config']['interval']
            store.put('monitor',m,m['revision'],db)


def tick(workflow,owner):
    schedule(workflow.store)
    job=workflow.store.claim(owner)
    if not job: return False
    try:
        workflow.execute(job)
        workflow.store.finish(job)
    except Exception as exc:
        from ask_common import AskError
        from ingest_ops import OpRefused
        safe=str(exc) if isinstance(exc,(Deferred,AskError,OpRefused,ValueError)) else 'Work incomplete; inspect configuration, source access or proposal validation'
        workflow.store.finish(job,safe,getattr(exc,'delay',min(3600,60*2**min(job['attempts'],6))))
        if getattr(exc,'pause',False) or job['attempts']>=5 or isinstance(exc,(ValueError,OpRefused)) and not isinstance(exc,Deferred):
            with workflow.store.connect() as db:
                db.execute("UPDATE jobs SET state='failed' WHERE id=? AND owner=?",(job['id'],owner))
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--backup',type=Path)
    args=parser.parse_args()
    store=Store(ROOT)
    if args.backup:
        store.backup(args.backup); return
    workflow=Workflow(ROOT,store)
    # One scheduler per state file. Job leases survive crashes; no service runs on import.
    with (store.path.parent/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        from ingest_server import wiki_write_lock
        with wiki_write_lock(): workflow.recover_publications()
        owner=identity('worker'); stopping=False
        def stop(*_):
            nonlocal stopping
            stopping=True
        signal.signal(signal.SIGTERM,stop)
        while not stopping:
            busy=tick(workflow,owner)
            if args.once: break
            if not busy: time.sleep(2)


if __name__=='__main__': main()
