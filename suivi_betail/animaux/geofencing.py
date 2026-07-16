from math import asin, cos, radians, sin, sqrt

RAYON_TERRE_KM = 6371.0


def _haversine_km(lat1, lng1, lat2, lng2):
    """Distance approximative en km entre deux points géographiques."""
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * RAYON_TERRE_KM * asin(min(1.0, sqrt(a)))


def _point_dans_polygone(lat, lng, anneau):
    """Test d'appartenance point/polygone par lancé de rayon (ray casting).

    anneau = [[lng, lat], [lng, lat], ...] (anneau fermé ou non).
    """
    try:
        x, y = float(lng), float(lat)
    except (TypeError, ValueError):
        return False
    inside = False
    n = len(anneau)
    j = n - 1
    for i in range(n):
        xi, yi = float(anneau[i][0]), float(anneau[i][1])
        xj, yj = float(anneau[j][0]), float(anneau[j][1])
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def _extraire_geometries(polygone):
    """Retourne une liste de (type, données) à partir d'un GeoJSON ou format brut.

    Supporte : FeatureCollection, Feature, Polygon/MultiPolygon GeoJSON,
    cercle custom {'type':'circle','coordinates':[lng,lat],'radius':m}
    et un simple anneau de coordonnées [[lng,lat], ...].
    """
    if not polygone:
        return []

    if isinstance(polygone, dict):
        t = polygone.get('type')
        if t == 'FeatureCollection':
            geoms = []
            for f in polygone.get('features', []):
                geoms.extend(_extraire_geometries(f.get('geometry', f)))
            return geoms
        if t == 'Feature':
            return _extraire_geometries(polygone.get('geometry', {}))
        if t == 'circle' or ('coordinates' in polygone and 'radius' in polygone):
            return [('circle', polygone)]
        if t == 'Polygon':
            return [('polygon', polygone.get('coordinates', []))]
        if t == 'MultiPolygon':
            geoms = []
            for poly in polygone.get('coordinates', []):
                geoms.append(('polygon', poly))
            return geoms
        return []

    if isinstance(polygone, (list, tuple)):
        # Anneau brut de coordonnées
        if len(polygone) >= 3 and all(
            isinstance(c, (list, tuple)) and len(c) >= 2 for c in polygone
        ):
            return [('ring', polygone)]
        return []

    return []


def _contient_zone(geom, lat, lng):
    """Indique si le point est contenu dans la géométrie de zone."""
    gtype, data = geom
    try:
        if gtype == 'circle':
            clng, clat = data['coordinates']
            rayon_km = float(data.get('radius', 0)) / 1000.0
            return _haversine_km(lat, lng, float(clat), float(clng)) <= rayon_km
        if gtype == 'polygon':
            # coordinates[0] = anneau extérieur
            anneaux = data[0] if data else []
            return _point_dans_polygone(lat, lng, anneaux)
        if gtype == 'ring':
            return _point_dans_polygone(lat, lng, data)
    except Exception:
        return False
    return False


def verifier_geofencing(lat, lng, animal):
    """Vérifie si l'animal est dans l'une de ses zones autorisées.

    Retourne {'hors_zone': bool, 'zones_hors': [{'nom','id'}, ...]}.
    L'animal est considéré hors zone s'il n'est dans AUCUNE zone valide.
    """
    if not animal or not animal.zone:
        return {'hors_zone': False, 'zones_hors': []}

    zone = animal.zone
    if zone.type_zone not in ['PATURAGE', 'STABULATION']:
        return {'hors_zone': False, 'zones_hors': []}

    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        return {'hors_zone': False, 'zones_hors': []}

    geoms = _extraire_geometries(zone.polygone)
    if not geoms:
        return {'hors_zone': False, 'zones_hors': []}

    if any(_contient_zone(g, lat, lng) for g in geoms):
        return {'hors_zone': False, 'zones_hors': []}

    return {
        'hors_zone': True,
        'zones_hors': [{'nom': zone.nom, 'id': zone.id}],
    }
