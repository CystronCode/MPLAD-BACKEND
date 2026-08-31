# backend/app/audit/hash_chain.py
# Cryptographic Append-Only Hash Chain for MEEV Investigation Actions

import hashlib
import json
from datetime import datetime, date
from typing import Dict, Any

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def compute_record_hash(
    payload: Dict[str, Any],
    actor_id: str,
    recorded_at: Any,
    previous_hash: str
) -> str:
    """
    Computes CurrentHash = SHA-256(canonical_json(payload) || actor_id || timestamp || previous_hash)
    """
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    timestamp_str = recorded_at.isoformat() if hasattr(recorded_at, "isoformat") else str(recorded_at)
    raw_data = f"{payload_str}:{actor_id}:{timestamp_str}:{previous_hash}".encode("utf-8")
    return hashlib.sha256(raw_data).hexdigest()

def verify_audit_chain(records: list[Dict[str, Any]]) -> bool:
    """
    Verifies that all entries in the audit trail chain correctly without retroactive tampering.
    """
    if not records:
        return True
        
    expected_prev = GENESIS_HASH
    for r in records:
        if r.get("previous_hash") != expected_prev:
            return False
            
        calculated = compute_record_hash(
            payload=r.get("payload", {}),
            actor_id=r.get("actor_id", ""),
            recorded_at=r.get("recorded_at"),
            previous_hash=expected_prev
        )
        
        if calculated != r.get("current_hash"):
            return False
            
        expected_prev = calculated
        
    return True
