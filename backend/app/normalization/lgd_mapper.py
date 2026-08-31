def get_attribute(item, attr_name):
    """Utility to retrieve an attribute or key from either a dict or model object."""
    if isinstance(item, dict):
        return item.get(attr_name)
    return getattr(item, attr_name, None)

def filter_by_district(candidates: list, district_lgd_code: int) -> list:
    """Stage 1: Hard Administrative Blocking by District LGD code.
    
    Filters the input candidate list to only those matches sharing the same district_lgd_code.
    """
    if district_lgd_code is None:
        return candidates
    return [c for c in candidates if get_attribute(c, "district_lgd_code") == district_lgd_code]

def filter_by_block(candidates: list, block_lgd_code: int | None) -> list:
    """Stage 2: Block & Sub-District Gating.
    
    Further narrows down candidates by block_lgd_code if one is explicitly provided.
    """
    if block_lgd_code is None:
        return candidates
    return [c for c in candidates if get_attribute(c, "block_lgd_code") == block_lgd_code]
