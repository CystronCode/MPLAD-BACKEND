import math

def haversine_distance(coords1: tuple[float, float] | None, coords2: tuple[float, float] | None) -> float | None:
    """Calculate the great-circle distance between two points in meters using Haversine formula."""
    if not coords1 or not coords2:
        return None
        
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    
    R = 6371000.0  # Mean radius of Earth in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def get_coords(item):
    """Retrieve latitude and longitude as a float tuple from dict or object."""
    if isinstance(item, dict):
        lat = item.get("latitude")
        lon = item.get("longitude")
    else:
        lat = getattr(item, "latitude", None)
        lon = getattr(item, "longitude", None)
        
    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon)
        except (ValueError, TypeError):
            return None
    return None

def to_dict(obj):
    """Convert an object or SQLAlchemy model to a standard dictionary."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__table__"):
        return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return obj

def reverse_spatial_lookup(project_coords: tuple[float, float] | None, candidates: list) -> tuple[dict | None, float | None]:
    """Stage 6 Reverse Spatial Fallback.
    
    If the string similarity was low, but a school campus is located within a 300m radius
    of the project's reported GPS coordinates, match to the closest school campus.
    """
    if not project_coords:
        return None, None
        
    closest_candidate = None
    min_dist = float("inf")
    
    for cand in candidates:
        cand_coords = get_coords(cand)
        if not cand_coords:
            continue
            
        dist = haversine_distance(project_coords, cand_coords)
        if dist is not None and dist < min_dist:
            min_dist = dist
            closest_candidate = cand
            
    if min_dist <= 300.0:
        return to_dict(closest_candidate), min_dist
        
    return None, None
