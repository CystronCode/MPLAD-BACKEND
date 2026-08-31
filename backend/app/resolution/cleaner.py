import re

ABBREVIATIONS = {
    r"\bgsss\b": "government senior secondary school",
    r"\bghs\b": "government high school",
    r"\bgps\b": "government primary school",
    r"\bgms\b": "government middle school",
    r"\bgss\b": "government senior school",
    r"\bgovt\b": "government",
    r"\bhs\b": "high school",
    r"\bps\b": "primary school",
    r"\bms\b": "middle school",
    r"\bsss\b": "senior secondary school",
    r"\bpvt\b": "private",
    r"\bsch\b": "school",
}

NOISE_PATTERNS = [
    r"\bconst(?:ruction)?\s+of\b",
    r"\bestablishment\s+of\b",
    r"\bsetup\s+of\b",
    r"\bsupply\s+of\b",
    r"\badditional\b",
    r"\bclass\s*rooms?\b",
    r"\brooms?\b",
    r"\btoilets?\b",
    r"\bsanitation\b",
    r"\bdrinking\s+water\b",
    r"\bcomputer\s+lab\b",
    r"\bward\s+(?:no\s*)?\d+\b",
    r"\bblock\s*(?:-)?\d+\b",
]

def clean_and_expand_school_name(text: str) -> str:
    """Strips administrative noise and normalizes/expands school acronyms.
    
    E.g. "GHS Rampur" -> "government high school rampur"
    "const of 2 class rooms at G.S.S.S. Palampur" -> "government senior secondary school palampur"
    """
    if not text:
        return ""
        
    t = text.lower()
    
    # Standardize dotted acronyms to simple strings first
    t = re.sub(r"\b(g)\.(s)\.(s)\.(s)\.\b", r"\1\2\3\4", t)
    t = re.sub(r"\b(g)\.(h)\.(s)\.\b", r"\1\2\3", t)
    t = re.sub(r"\b(g)\.(p)\.(s)\.\b", r"\1\2\3", t)
    t = re.sub(r"\b(g)\.(m)\.(s)\.\b", r"\1\2\3", t)
    t = re.sub(r"\b(g)\.(s)\.(s)\.\b", r"\1\2\3", t)
    
    # Strip common administrative noise prefixes/suffixes
    for pattern in NOISE_PATTERNS:
        t = re.sub(pattern, " ", t)
        
    # Expand standard abbreviations on word boundaries
    for pattern, replacement in ABBREVIATIONS.items():
        t = re.sub(pattern, replacement, t)
        
    # Clean up punctuation and consolidate whitespace
    t = re.sub(r"[^\w\s]", " ", t)
    t = " ".join(t.split())
    return t
