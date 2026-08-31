import math
import jellyfish
from backend.app.normalization.lgd_mapper import filter_by_district, filter_by_block, get_attribute
from backend.app.resolution.cleaner import clean_and_expand_school_name
from backend.app.resolution.spatial_fallback import haversine_distance, reverse_spatial_lookup, to_dict, get_coords

# Common school indicator terms to verify text references a school before matching
SCHOOL_INDICATORS = [
    "school", "sch", "academy", "vidyalaya", "pathshala", "college", "institute", 
    "ghs", "gps", "gsss", "gms", "gss", "hs", "ps", "ms", "sss", "high", "primary", "secondary", "middle", "senior"
]

def contains_school_token(text: str) -> bool:
    """Check if the text contains any standard school indicator tokens."""
    if not text:
        return False
    text_lower = text.lower()
    return any(ind in text_lower for ind in SCHOOL_INDICATORS)

def get_soundex_tokens(text: str) -> set[str]:
    """Generate a set of Soundex codes for words in the cleaned text."""
    words = [w for w in text.split() if len(w) > 1]
    if not words:
        words = text.split()
        
    codes = set()
    for w in words:
        try:
            code = jellyfish.soundex(w)
            if code:
                codes.add(code)
        except Exception:
            pass
    return codes

def phonetic_similarity(text1: str, text2: str) -> float:
    """Calculate phonetic similarity as the Jaccard index of Soundex tokens."""
    codes1 = get_soundex_tokens(text1)
    codes2 = get_soundex_tokens(text2)
    if not codes1 or not codes2:
        return 0.0
        
    intersection = codes1.intersection(codes2)
    union = codes1.union(codes2)
    return len(intersection) / len(union)

def proper_name_similarity(text1: str, text2: str) -> float:
    """Calculate Jaro-Winkler similarity on the core proper names of schools.
    
    Excludes common administrative and institutional suffixes/prefixes (e.g. government, school, high).
    """
    terms = {"government", "high", "school", "primary", "senior", "secondary", "middle", "academy", "public", "private", "aided", "unaided", "memorial"}
    words1 = [w for w in text1.split() if w not in terms]
    words2 = [w for w in text2.split() if w not in terms]
    p1 = " ".join(words1)
    p2 = " ".join(words2)
    if not p1 or not p2:
        return 0.0
    return jellyfish.jaro_winkler_similarity(p1, p2)

def calculate_composite_match_score(
    project_text_clean: str = None,
    candidate_name_clean: str = None,
    project_coords: tuple[float, float] | None = None,
    candidate_coords: tuple[float, float] | None = None,
    project_text_raw: str = None,
    candidate_name_raw: str = None,
    **kwargs
) -> tuple[float, str]:
    """Compute the combined lexical + phonetic match score, gated by spatial distance."""
    p_text = project_text_clean or project_text_raw or ""
    c_name = candidate_name_clean or candidate_name_raw or ""
    
    p_clean = clean_and_expand_school_name(p_text) if p_text else ""
    c_clean = clean_and_expand_school_name(c_name) if c_name else ""

    # 1. Lexical Similarity (Jaro-Winkler)
    lex_score = jellyfish.jaro_winkler_similarity(p_clean, c_clean)
    
    # 2. Phonetic Similarity (Soundex Jaccard)
    phon_score = phonetic_similarity(p_clean, c_clean)
    
    # Base Weighted Score (70% Lexical + 30% Phonetic)
    base_score = 0.70 * lex_score + 0.30 * phon_score
    
    # 3. Stage 5 Spatial Gating & Reverse Spatial Fallback
    if project_coords and candidate_coords:
        dist = haversine_distance(project_coords, candidate_coords)
        if dist is None:
            spatial_mult = 1.0
        elif dist <= 200.0:
            spatial_mult = 1.10  # 10% bonus
        elif dist <= 1000.0:
            spatial_mult = 1.00  # neutral
        elif dist <= 5000.0:
            spatial_mult = 0.75  # penalty
        else:
            return (0.0, "SPATIAL_REJECT_OUT_OF_BOUNDS")
            
        # Reverse Spatial Fallback for Renamed Schools
        if base_score < 0.70 and dist <= 300.0:
            return (0.86, "ACCEPTED_VIA_REVERSE_SPATIAL_FALLBACK")
            
        score = base_score * spatial_mult
    else:
        score = base_score
        
    final_score = min(1.0, max(0.0, score))
    
    if final_score >= 0.85:
        status = "AUTO_ACCEPTED"
    elif final_score >= 0.60:
        status = "ROUTED_TO_AMBIGUITY_QUEUE"
    else:
        status = "UNRESOLVED_LOW_CONFIDENCE"
        
    return (final_score, status)

def resolve_project(
    project_text: str,
    project_coords: tuple[float, float] | None,
    candidates: list,
    district_lgd_code: int | None = None,
    block_lgd_code: int | None = None
) -> dict:
    """Executes the 7-Stage Entity Resolution workflow.
    
    Returns the resolved school, confidence score, status, and resolution reasoning.
    """
    # Initialize default output format
    result = {
        "udise_code": None,
        "school": None,
        "confidence": 0.0,
        "status": "UNRESOLVED",
        "reason": "UNRESOLVED_LOW_CONFIDENCE"
    }
    
    # Guard case: If project description lacks school indicators, reject immediately
    if not contains_school_token(project_text):
        return result

    # STAGE 1: Hard Administrative Blocking (District)
    if district_lgd_code is not None:
        candidates = filter_by_district(candidates, district_lgd_code)
        
    # STAGE 2: Block & Sub-District Gating
    if block_lgd_code is not None:
        candidates = filter_by_block(candidates, block_lgd_code)
        
    if not candidates:
        return result

    # STAGE 3: Token Cleaning & Expansion
    proj_clean = clean_and_expand_school_name(project_text)
    
    # STAGE 4: Lexical & Phonetic Matching (Check for strong lexical name matches first)
    best_lexical_cand = None
    best_lexical_score = -1.0
    
    for cand in candidates:
        cand_name = get_attribute(cand, "name_canonical")
        cand_clean = clean_and_expand_school_name(cand_name)
        
        lex_score = jellyfish.jaro_winkler_similarity(proj_clean, cand_clean)
        phon_score = phonetic_similarity(proj_clean, cand_clean)
        base_score = 0.70 * lex_score + 0.30 * phon_score
        
        if base_score > best_lexical_score:
            best_lexical_score = base_score
            best_lexical_cand = cand

    # STAGE 5: Spatial Gating
    best_cand = None
    best_score = -1.0
    best_dist = None

    if best_lexical_cand is not None and best_lexical_score >= 0.75:
        cand_coords = get_coords(best_lexical_cand)
        if project_coords and cand_coords:
            dist = haversine_distance(project_coords, cand_coords)
            if dist is not None and dist > 5000.0:
                # Reject candidate > 5km away
                return {
                    "udise_code": None,
                    "school": None,
                    "confidence": 0.0,
                    "status": "UNRESOLVED",
                    "reason": "SPATIAL_REJECT_OUT_OF_BOUNDS"
                }
            elif dist is not None and dist <= 200.0:
                spatial_mult = 1.10
            elif dist is not None and dist <= 1000.0:
                spatial_mult = 1.00
            elif dist is not None and dist <= 5000.0:
                spatial_mult = 0.75
            else:
                spatial_mult = 1.0
                
            best_score = best_lexical_score * spatial_mult
            best_dist = dist
        else:
            best_score = best_lexical_score
            best_dist = None
            
        best_cand = best_lexical_cand
        best_score = min(1.0, max(0.0, best_score))
    else:
        # If there is no strong name match, evaluate all candidates by composite score
        for cand in candidates:
            cand_name = get_attribute(cand, "name_canonical")
            cand_clean = clean_and_expand_school_name(cand_name)
            cand_coords = get_coords(cand)
            
            score, _ = calculate_composite_match_score(
                proj_clean,
                cand_clean,
                project_coords,
                cand_coords
            )
            
            if score > best_score:
                best_score = score
                best_cand = cand
                if project_coords and cand_coords:
                    best_dist = haversine_distance(project_coords, cand_coords)

    # STAGE 6: Reverse Spatial Fallback (Renamed / Merged School)
    if project_coords:
        # Evaluate proper name similarity to check if fallback is necessary
        proper_sim = 1.0
        if best_cand:
            best_cand_name = get_attribute(best_cand, "name_canonical")
            best_cand_clean = clean_and_expand_school_name(best_cand_name)
            proper_sim = proper_name_similarity(proj_clean, best_cand_clean)
            
        if best_cand is None or (best_score < 0.85 and proper_sim < 0.50):
            fallback_cand, fallback_dist = reverse_spatial_lookup(project_coords, candidates)
            if fallback_cand:
                best_cand = fallback_cand
                best_score = 0.86
                best_dist = fallback_dist

    # Check if a resolution has occurred
    if best_cand is not None and best_score > 0.0:
        cand_dict = to_dict(best_cand)
        udise_code = cand_dict.get("udise_code")
        
        if best_dist is not None and best_dist > 5000.0:
            return {
                "udise_code": None,
                "school": None,
                "confidence": 0.0,
                "status": "UNRESOLVED",
                "reason": "SPATIAL_REJECT_OUT_OF_BOUNDS"
            }

        # STAGE 7: Confidence Threshold Routing
        if best_score >= 0.85:
            status = "AUTO_ACCEPTED"
            reason = "AUTO_ACCEPTED"
        elif best_score >= 0.60:
            status = "AMBIGUOUS"
            reason = "ROUTED_TO_AMBIGUITY_QUEUE"
        else:
            status = "UNRESOLVED"
            reason = "UNRESOLVED_LOW_CONFIDENCE"
            
        return {
            "udise_code": udise_code,
            "school": cand_dict,
            "confidence": round(float(best_score), 3),
            "status": status,
            "reason": reason
        }
        
    return result
