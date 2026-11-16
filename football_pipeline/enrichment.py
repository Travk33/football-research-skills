"""Add explicit sourced observations to a new bundle without rewriting old evidence."""
from copy import deepcopy
from datetime import datetime, timezone
from .request import fingerprint


def _time(value):
    if not isinstance(value,str): raise ValueError('observation time required')
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None: raise ValueError('observation time needs timezone')
    return parsed.astimezone(timezone.utc)


def merge_evidence(bundle,supplement):
    if supplement.get('evidenceHash') != fingerprint(bundle):
        raise ValueError('supplement does not identify this evidence bundle')
    result=deepcopy(bundle); now=datetime.now(timezone.utc)
    rows=supplement.get('fixtures')
    if not isinstance(rows,list): raise ValueError('supplement fixtures must be a list')
    by_id={f['id']:f for f in result['fixtures']}; seen=set()
    for row in rows:
        fid=row.get('id')
        if fid not in by_id or fid in seen: raise ValueError('unknown or duplicate supplement fixture')
        seen.add(fid); fixture=by_id[fid]
        if now >= _time(fixture['kickoffUtc']): raise ValueError('cannot enrich a pre-match fixture after kickoff')
        if set(row)-{'id','news','quotes','lineup'}: raise ValueError('unsupported supplement fields')
        snapshot=fixture.setdefault('snapshot',{})
        for field in ('news','quotes','lineup'):
            if field not in row: continue
            records=[row[field]] if field=='lineup' else row[field]
            if not isinstance(records,list): raise ValueError(field+' must be a list')
            for item in records:
                if not isinstance(item,dict) or str(item.get('fixtureId')) != fid:
                    raise ValueError('observation fixture ID mismatch')
                if not isinstance(item.get('source'),str) or not item['source'].strip():
                    raise ValueError('each observation requires its source')
                if _time(item.get('observedAt')) > now: raise ValueError('future observation time')
                fixture.setdefault('sources',[]).append({'url':item['source'],'retrievedAt':item['observedAt'],'sourceType':'supplied-observation'})
            if field=='lineup': snapshot[field]=deepcopy(records[0])
            else: snapshot[field]=snapshot.get(field,[])+deepcopy(records)
    result['previousEvidenceHash']=fingerprint(bundle)
    result['enrichedAt']=now.isoformat()
    result.setdefault('originalCollectedAt',bundle['collectedAt'])
    result['collectedAt']=now.isoformat()
    # Bundle assembly time advances; individual sources and snapshots keep their true observation times.
    return result
