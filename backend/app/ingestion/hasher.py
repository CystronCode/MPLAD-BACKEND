import hashlib
import json

def compute_sha256_bytes(data: bytes) -> str:
    """Compute the SHA-256 digest of a bytes object, returning a 64-character hex string."""
    return hashlib.sha256(data).hexdigest()

def compute_sha256_dict(record: dict) -> str:
    """Compute a deterministic SHA-256 digest of a dictionary payload.
    
    This converts the dictionary to a canonical JSON string (keys sorted, compact separators)
    before encoding to UTF-8 and hashing.
    """
    canonical_json = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
    return compute_sha256_bytes(canonical_json.encode("utf-8"))
