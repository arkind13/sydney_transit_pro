# station_lookup.py
"""
Pre-loaded Sydney Trains station dictionary for instant geocoding
— no API call needed for any station name lookup.

Covers all 180+ stations on the Sydney Trains network.
Coordinates sourced from TfNSW Open Data & verified against app presets.
"""

# =============================================================================
# ALL SYDNEY TRAINS STATIONS (alphabetical)
# Format: "Station Name": (latitude, longitude)
# =============================================================================

STATION_COORDS: dict[str, tuple[float, float]] = {
    # ── A ──────────────────────────────────────────────────────────────
    "Allawah":               (-33.9697, 151.1145),
    "Arncliffe":             (-33.9362, 151.1473),
    "Artarmon":              (-33.8088, 151.1851),
    "Ashfield":              (-33.8876, 151.1259),
    "Asquith":               (-33.6887, 151.1081),
    "Auburn":                (-33.8492, 151.0329),

    # ── B ──────────────────────────────────────────────────────────────
    "Banksia":               (-33.9453, 151.1404),
    "Bankstown":             (-33.9179, 151.0341),
    "Bardwell Park":         (-33.9316, 151.1249),
    "Beecroft":              (-33.7497, 151.0664),
    "Bella Vista":           (-33.7306, 150.9440),
    "Belmore":               (-33.9172, 151.0883),
    "Berala":                (-33.8716, 151.0323),
    "Berowra":               (-33.6235, 151.1532),
    "Beverly Hills":         (-33.9490, 151.0812),
    "Bexley North":          (-33.9375, 151.1135),
    "Birrong":               (-33.8933, 151.0240),
    "Blacktown":             (-33.7686, 150.9074),
    "Bondi Junction":        (-33.8910, 151.2485),
    "Burwood":               (-33.8772, 151.1043),

    # ── C ──────────────────────────────────────────────────────────────
    "Cabramatta":            (-33.8946, 150.9391),
    "Campbelltown":          (-34.0641, 150.8141),
    "Campsie":               (-33.9104, 151.1034),
    "Canley Vale":           (-33.8872, 150.9436),
    "Canterbury":            (-33.9119, 151.1186),
    "Caringbah":             (-34.0416, 151.1226),
    "Carlton":               (-33.9682, 151.1240),
    "Carramar":              (-33.8843, 150.9615),
    "Castle Hill":           (-33.7316, 151.0073),
    "Casula":                (-33.9499, 150.9120),
    "Central":               (-33.8832, 151.2070),
    "Chatswood":             (-33.7980, 151.1809),
    "Cheltenham":            (-33.7560, 151.0660),
    "Cherrybrook":           (-33.7367, 151.0320),
    "Chester Hill":          (-33.8836, 150.9999),
    "Circular Quay":         (-33.8612, 151.2107),
    "Clarendon":             (-33.6085, 150.7879),
    "Clyde":                 (-33.8358, 151.0169),
    "Como":                  (-34.0044, 151.0681),
    "Concord West":          (-33.8485, 151.0856),
    "Cronulla":              (-34.0557, 151.1515),
    "Croydon":               (-33.8832, 151.1151),

    # ── D ──────────────────────────────────────────────────────────────
    "Denistone":             (-33.7996, 151.0868),
    "Domestic Airport":      (-33.9336, 151.1811),
    "Doonside":              (-33.7637, 150.8692),
    "Dulwich Hill":          (-33.9111, 151.1412),

    # ── E ──────────────────────────────────────────────────────────────
    "East Hills":            (-33.9618, 150.9847),
    "East Richmond":         (-33.6030, 150.7570),
    "Eastwood":              (-33.7901, 151.0822),
    "Edgecliff":             (-33.8797, 151.2367),
    "Edmondson Park":        (-33.9693, 150.8587),
    "Emu Plains":            (-33.7457, 150.6714),
    "Engadine":              (-34.0677, 151.0147),
    "Epping":                (-33.7727, 151.0820),
    "Erskineville":          (-33.9001, 151.1856),

    # ── F ──────────────────────────────────────────────────────────────
    "Fairfield":             (-33.8724, 150.9568),
    "Flemington":            (-33.8650, 151.0702),

    # ── G ──────────────────────────────────────────────────────────────
    "Glenfield":             (-33.9722, 150.8931),
    "Gordon":                (-33.7558, 151.1544),
    "Granville":             (-33.8328, 151.0119),
    "Green Square":          (-33.9062, 151.2025),
    "Guildford":             (-33.8542, 150.9844),
    "Gymea":                 (-34.0349, 151.0854),

    # ── H ──────────────────────────────────────────────────────────────
    "Harris Park":           (-33.8233, 151.0076),
    "Heathcote":             (-34.0880, 151.0081),
    "Helensburgh":           (-34.1769, 150.9949),
    "Hills Showground":      (-33.7279, 150.9870),
    "Holsworthy":            (-33.9632, 150.9567),
    "Homebush":              (-33.8668, 151.0865),
    "Hornsby":               (-33.7035, 151.0984),
    "Hurlstone Park":        (-33.9102, 151.1325),
    "Hurstville":            (-33.9673, 151.1024),

    # ── I ──────────────────────────────────────────────────────────────
    "Ingleburn":             (-33.9977, 150.8642),
    "International Airport": (-33.9353, 151.1668),

    # ── J ──────────────────────────────────────────────────────────────
    "Jannali":               (-34.0159, 151.0646),

    # ── K ──────────────────────────────────────────────────────────────
    "Kellyville":            (-33.7134, 150.9351),
    "Killara":               (-33.7655, 151.1617),
    "Kings Cross":           (-33.8745, 151.2221),
    "Kingsgrove":            (-33.9406, 151.1005),
    "Kingswood":             (-33.7584, 150.7205),
    "Kirrawee":              (-34.0350, 151.0715),
    "Kogarah":               (-33.9627, 151.1324),

    # ── L ──────────────────────────────────────────────────────────────
    "Lakemba":               (-33.9201, 151.0759),
    "Leightonfield":         (-33.8815, 150.9847),
    "Leppington":            (-33.9544, 150.8080),
    "Leumeah":               (-34.0508, 150.8306),
    "Lewisham":              (-33.8932, 151.1474),
    "Lidcombe":              (-33.8636, 151.0447),
    "Lindfield":             (-33.7756, 151.1691),
    "Liverpool":             (-33.9243, 150.9272),
    "Loftus":                (-34.0451, 151.0512),

    # ── M ──────────────────────────────────────────────────────────────
    "Macarthur":             (-34.0720, 150.7973),
    "Macdonaldtown":         (-33.8968, 151.1863),
    "Macquarie Fields":      (-33.9847, 150.8791),
    "Macquarie Park":        (-33.7852, 151.1283),
    "Macquarie University":  (-33.7771, 151.1180),
    "Marayong":              (-33.7463, 150.9002),
    "Marrickville":          (-33.9138, 151.1532),
    "Martin Place":          (-33.8679, 151.2118),
    "Mascot":                (-33.9233, 151.1874),
    "Meadowbank":            (-33.8160, 151.0901),
    "Merrylands":            (-33.8365, 150.9926),
    "Milsons Point":         (-33.8459, 151.2118),
    "Minto":                 (-34.0273, 150.8425),
    "Miranda":               (-34.0363, 151.1026),
    "Mortdale":              (-33.9706, 151.0813),
    "Mount Colah":           (-33.6715, 151.1149),
    "Mount Druitt":          (-33.7696, 150.8201),
    "Mount Kuring-gai":      (-33.6532, 151.1369),
    "Mulgrave":              (-33.6266, 150.8305),
    "Museum":                (-33.8766, 151.2093),

    # ── N ──────────────────────────────────────────────────────────────
    "Narwee":                (-33.9476, 151.0702),
    "Newtown":               (-33.8980, 151.1796),
    "Normanhurst":           (-33.7209, 151.0972),
    "North Ryde":            (-33.7946, 151.1378),
    "North Strathfield":     (-33.8590, 151.0881),
    "North Sydney":          (-33.8411, 151.2072),
    "Norwest":               (-33.7346, 150.9636),

    # ── O ──────────────────────────────────────────────────────────────
    "Oatley":                (-33.9808, 151.0791),
    "Olympic Park":          (-33.8465, 151.0695),

    # ── P ──────────────────────────────────────────────────────────────
    "Padstow":               (-33.9519, 151.0324),
    "Panania":               (-33.9543, 150.9978),
    "Parramatta":            (-33.8175, 151.0050),
    "Pendle Hill":           (-33.8013, 150.9564),
    "Pennant Hills":         (-33.7381, 151.0725),
    "Penrith":               (-33.7501, 150.6958),
    "Penshurst":             (-33.9662, 151.0892),
    "Petersham":             (-33.8939, 151.1551),
    "Punchbowl":             (-33.9253, 151.0555),
    "Pymble":                (-33.7447, 151.1420),

    # ── Q ──────────────────────────────────────────────────────────────
    "Quakers Hill":          (-33.7274, 150.8862),

    # ── R ──────────────────────────────────────────────────────────────
    "Redfern":               (-33.8922, 151.1990),
    "Regents Park":          (-33.8830, 151.0241),
    "Revesby":               (-33.9524, 151.0149),
    "Rhodes":                (-33.8306, 151.0871),
    "Richmond":              (-33.5988, 150.7525),
    "Riverstone":            (-33.6791, 150.8604),
    "Riverwood":             (-33.9515, 151.0525),
    "Rockdale":              (-33.9523, 151.1367),
    "Rooty Hill":            (-33.7716, 150.8452),
    "Roseville":             (-33.7842, 151.1773),
    "Rouse Hill":            (-33.6920, 150.9243),

    # ── S ──────────────────────────────────────────────────────────────
    "Schofields":            (-33.7046, 150.8739),
    "Sefton":                (-33.8852, 151.0115),
    "Seven Hills":           (-33.7743, 150.9362),
    "St James":              (-33.8707, 151.2104),
    "St Leonards":           (-33.8224, 151.1942),
    "St Marys":              (-33.7621, 150.7751),
    "St Peters":             (-33.9075, 151.1803),
    "Stanmore":              (-33.8947, 151.1639),
    "Strathfield":           (-33.8715, 151.0940),
    "Summer Hill":           (-33.8904, 151.1387),
    "Sutherland":            (-34.0315, 151.0573),
    "Sydenham":              (-33.9148, 151.1660),

    # ── T ──────────────────────────────────────────────────────────────
    "Tallawong":             (-33.6916, 150.9060),
    "Tempe":                 (-33.9245, 151.1564),
    "Thornleigh":            (-33.7318, 151.0784),
    "Toongabbie":            (-33.7872, 150.9515),
    "Town Hall":             (-33.8732, 151.2071),
    "Turramurra":            (-33.7323, 151.1284),
    "Turrella":              (-33.9299, 151.1400),

    # ── V ──────────────────────────────────────────────────────────────
    "Villawood":             (-33.8809, 150.9761),
    "Vineyard":              (-33.6504, 150.8511),

    # ── W ──────────────────────────────────────────────────────────────
    "Wahroonga":             (-33.7175, 151.1170),
    "Waitara":               (-33.7101, 151.1044),
    "Warrawee":              (-33.7242, 151.1217),
    "Warwick Farm":          (-33.9131, 150.9352),
    "Waterfall":             (-34.1345, 150.9945),
    "Waverton":              (-33.8378, 151.1976),
    "Wentworthville":        (-33.8071, 150.9727),
    "Werrington":            (-33.7592, 150.7577),
    "West Ryde":             (-33.8073, 151.0902),
    "Westmead":              (-33.8084, 150.9879),
    "Wiley Park":            (-33.9227, 151.0681),
    "Windsor":               (-33.6138, 150.8113),
    "Wolli Creek":           (-33.9286, 151.1541),
    "Wollstonecraft":        (-33.8319, 151.1918),
    "Woolooware":            (-34.0477, 151.1441),
    "Wynyard":               (-33.8660, 151.2056),

    # ── Y ──────────────────────────────────────────────────────────────
    "Yagoona":               (-33.9070, 151.0245),
    "Yennora":               (-33.8647, 150.9708),
}


# ─────────────────────────────────────────────────────────────────────
#  LOOKUP HELPERS
# ─────────────────────────────────────────────────────────────────────

def find_station_coords(query: str) -> tuple[float, float] | None:
    """
    Try to match a user query to a known station.
    Returns (lat, lng) or None.

    Tries: exact match → case-insensitive → substring match.
    """
    if not query or not query.strip():
        return None

    q = query.strip()

    # 1. Exact match
    if q in STATION_COORDS:
        return STATION_COORDS[q]

    # 2. Case-insensitive
    q_lower = q.lower()
    for name, coords in STATION_COORDS.items():
        if name.lower() == q_lower:
            return coords

    # 3. Remove "Station" / "Train Station" suffix and try again
    cleaned = q_lower
    for suffix in (" train station", " station", " railway station"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break
    for name, coords in STATION_COORDS.items():
        if name.lower() == cleaned:
            return coords

    # 4. Substring match (query is part of the station name)
    for name, coords in STATION_COORDS.items():
        if q_lower in name.lower():
            return coords

    # 5. Station name is part of the query (e.g. "Mount Druitt Train Station")
    for name, coords in STATION_COORDS.items():
        if name.lower() in q_lower:
            return coords

    return None


def get_station_name(query: str) -> str | None:
    """
    Like find_station_coords but returns the canonical station name.
    Useful for cleaning user input before passing to TfNSW API.
    """
    if not query or not query.strip():
        return None

    q = query.strip()

    if q in STATION_COORDS:
        return q

    q_lower = q.lower()
    for name in STATION_COORDS:
        if name.lower() == q_lower:
            return name

    cleaned = q_lower
    for suffix in (" train station", " station", " railway station"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break
    for name in STATION_COORDS:
        if name.lower() == cleaned:
            return name

    for name in STATION_COORDS:
        if q_lower in name.lower():
            return name

    for name in STATION_COORDS:
        if name.lower() in q_lower:
            return name

    return None


def all_station_names() -> list[str]:
    """Return all known station names (sorted)."""
    return sorted(STATION_COORDS.keys())
