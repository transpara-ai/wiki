"""Host-side workplace connector extension contract (no workplace enrollment).

Adapters must be installed and registered in trusted host code. Monitor input
cannot name a Python module or execute a connector. Built-in collectors continue
to use knowledge_sources; this contract gives later workplace adapters the same
capture/checkpoint boundary without extending browser authority.
"""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Capture:
    source: str
    original: bytes
    extracted: str
    metadata: dict


@dataclass(frozen=True)
class Batch:
    captures: tuple[Capture,...]
    checkpoint: dict
    complete: bool
    deferred_reason: str | None = None


class Connector(Protocol):
    def preview(self,config:dict,transport) -> dict: ...
    def collect(self,config:dict,checkpoint:dict,transport) -> Batch: ...


def retain_batch(store,monitor,batch):
    """Adapter reuse seam: durable captures and checkpoint move in one transaction."""
    if not batch.complete and not batch.deferred_reason:
        raise ValueError('Incomplete connector batches must expose deferred work')
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        current=store.get('monitor',monitor['id'],db)
        if current['revision']!=monitor['revision'] or current['state']!='enabled':
            raise ValueError('Monitor changed during collection')
        changed=[]
        for capture in batch.captures:
            key,meaningful=store.capture(capture.source,capture.original,capture.extracted,capture.metadata,monitor['id'],db)
            if meaningful: changed.append(key)
        current.update(checkpoint=batch.checkpoint,error=batch.deferred_reason,pending=0 if batch.complete else 1)
        store.put('monitor',current,current['revision'],db)
        return changed
