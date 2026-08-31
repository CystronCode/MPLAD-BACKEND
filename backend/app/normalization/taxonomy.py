import re
from enum import Enum

class CanonicalAssetType(str, Enum):
    ADDITIONAL_CLASSROOM = "ADDITIONAL_CLASSROOM"
    TOILET_BLOCK = "TOILET_BLOCK"
    DRINKING_WATER = "DRINKING_WATER"
    COMPUTER_LAB = "COMPUTER_LAB"
    SCIENCE_LAB = "SCIENCE_LAB"
    LIBRARY_ROOM = "LIBRARY_ROOM"
    BOUNDARY_WALL = "BOUNDARY_WALL"
    GENERIC_CIVIL_REPAIR = "GENERIC_CIVIL_REPAIR"

ASSET_TAXONOMY_RULES = [
    (CanonicalAssetType.ADDITIONAL_CLASSROOM, [
        r"(?:const(?:ruction)?|creation|addition|additional)\s+(?:of\s+)?(\d+)?\s*(?:addl\.?|additional)?\s*(?:class\s*rooms?|rooms?|clrms?|cr\b)",
        r"(\d+)\s*(?:additional\s+)?(?:class\s*rooms?|rooms?|clrms?)",
        r"(?:construction|const)\s+of\s+class\s*room",
        r"(?:school\s+room|classroom)"
    ]),
    (CanonicalAssetType.TOILET_BLOCK, [
        r"(?:const(?:ruction)?\s+of\s+)?(?:girls?|boys?|cwsn)?\s*(?:toilet|lavatory|urinal|sanitation)\s*(?:block|unit|complex|facility)?",
        r"(?:swachh\s*bharat|toilet|sanitation)\s*facility",
        r"drinking\s*water\s*and\s*toilet"
    ]),
    (CanonicalAssetType.COMPUTER_LAB, [
        r"(?:establishment|setup|supply\s+of)\s*(?:computers?\s*(?:and\s+setup\s+of\s*)?)?(?:smart\s*class|ict\s*lab|computer\s*lab|computers?|smart\s*ict\s*lab)",
        r"(?:setup|provision|supply|establishment|const(?:ruction)?).*(?:ict|computer|smart\s*class|cal\s*lab)",
        r"(?:cal\s*lab|digital\s*library|computer\s*room|ict\s*lab|computer\s*lab|smart\s*class)",
        r"smart\s*classroom"
    ]),
    (CanonicalAssetType.SCIENCE_LAB, [
        r"(?:establishment|setup|const(?:ruction)?\s+of)\s*(?:physics|chemistry|biology|science)\s*(?:science\s*)?(?:lab|laboratory)",
        r"(?:physics|chemistry|biology|science)\s*(?:science\s*)?(?:lab|laboratory)"
    ]),
    (CanonicalAssetType.LIBRARY_ROOM, [
        r"(?:const(?:ruction)?|setup)\s+of\s*(?:library|reading\s*room|book\s*bank)"
    ]),
    (CanonicalAssetType.BOUNDARY_WALL, [
        r"(?:const(?:ruction)?\s+of\s+)?(?:boundary\s*wall|compound\s*wall|fencing|barbed\s*wire)"
    ]),
    (CanonicalAssetType.DRINKING_WATER, [
        r"(?:installation|provision\s+of|provision)\s*(?:of\s+)?(?:ro\s*(?:drinking\s*water\s*)?plant|drinking\s*water|water\s*cooler|borewell|handpump|water\s*purifier)",
        r"(?:ro\s*plant|drinking\s*water|water\s*cooler|borewell|handpump|water\s*purifier)"
    ])
]

def normalize_asset_description(text: str) -> tuple[CanonicalAssetType, int]:
    """Extract canonical asset type and numerical quantities from description text.
    
    If no quantity is explicitly specified/captured, defaults to 1.
    If no taxonomy regex matches, defaults to GENERIC_CIVIL_REPAIR.
    """
    if not text:
        return CanonicalAssetType.GENERIC_CIVIL_REPAIR, 1
        
    text_lower = text.lower()
    for asset_type, patterns in ASSET_TAXONOMY_RULES:
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                quantity = 1
                for gp in match.groups():
                    if gp and gp.isdigit():
                        quantity = int(gp)
                        break
                return asset_type, quantity
                
    return CanonicalAssetType.GENERIC_CIVIL_REPAIR, 1
