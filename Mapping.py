team_map = {
    # ESPN API Name : EXACT BartTorvik CSV Name
    "Iowa State": "Iowa St.",
    "Purdue": "Purdue",
    "Indiana": "Indiana",
    "Wake Forest": "Wake Forest",
    "East Carolina": "East Carolina", # Check if your CSV says "E Carolina" or "East Carolina"
    "Mississippi State": "Mississippi St.",
    "Kansas": "Kansas",
    "Virginia": "Virginia",
    "Rutgers": "Rutgers",
    "FDU": "Fairleigh Dickinson",
    "TCU": "TCU",
    "Marquette": "Marquette",
    "U.C.S.B.": "UC Santa Barbara",
    "L.M.U.": "Loyola Marymount",
    "St. Thomas": "St. Thomas",
    "McNeese St.": "McNeese",
}

def clean_name(team_name):
    # This checks the map first, then returns the original if not found
    return team_map.get(team_name, team_name)