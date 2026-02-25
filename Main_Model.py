import pandas as pd
from datetime import datetime
import os
import glob


def load_all_data():
    """Load all required data files."""
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    try:
        kenpom_df = pd.read_csv('kenpom_stats.csv')
        print(f"\n1. ✓ Loaded {len(kenpom_df)} teams from KenPom")

        hca_df = pd.read_csv('hca_rankings.csv')
        print(f"2. ✓ Loaded {len(hca_df)} teams HCA data")

        barttorvik_df = pd.read_csv('barttorvik_splits.csv')
        print(f"3. ✓ Loaded {len(barttorvik_df)} teams shot data")

        # Find the newest games_*.csv file
        games_files = glob.glob('games_*.csv')
        if not games_files:
            raise FileNotFoundError("No games_*.csv file found")

        # Get the newest file by modification time
        newest_games_file = max(games_files, key=os.path.getmtime)
        games_df = pd.read_csv(newest_games_file)

        # Extract date from filename
        games_date = newest_games_file.replace('games_', '').replace('.csv', '')

        print(f"4. ✓ Loaded {len(games_df)} games from {newest_games_file}")

        return kenpom_df, hca_df, barttorvik_df, games_df, games_date
    except FileNotFoundError as e:
        print(f"✗ Error: Could not find file - {e.filename}")
        return None, None, None, None, None


def clean_team_name_simple(name):
    """Simplified clean for matching - removes mascots and normalizes."""
    if pd.isna(name):
        return ""

    name = str(name).strip()

    # Remove common mascots
    mascots = [
        ' Bulldogs', ' Tigers', ' Eagles', ' Bears', ' Wildcats', ' Lions',
        ' Panthers', ' Cougars', ' Cardinals', ' Spartans', ' Trojans',
        ' Knights', ' Warriors', ' Rams', ' Huskies', ' Bruins', ' Buckeyes',
        ' Volunteers', ' Aggies', ' Bulls', ' Terrapins', ' Paladins',
        ' Shockers', ' Bearcats', ' Golden Gophers', ' Hawkeyes', ' Wolverines',
        ' Red Raiders', ' Mountaineers', ' Green Wave', ' 49ers', ' Blazers',
        ' Owls', ' Nittany Lions', ' Golden Hurricane', ' Salukis', ' Musketeers',
        ' Bison', ' Midshipmen', ' Red Flash', ' Colonels', ' Demons', ' Vaqueros',
        ' Beacons', ' Cowboys', ' Lumberjacks', ' Hornets', ' Redbirds',
        ' Purple Aces', ' Braves', ' Seahawks', ' Islanders', ' Privateers',
        ' Ducks', ' Hoosiers', ' Jayhawks', ' Jaguars', ' Racers', ' Wolfpack',
        ' Mustangs', ' Sycamores', ' Rattlers', ' Red Storm', ' Golden Lions',
        ' Delta Devils', ' Boilermakers', ' Cornhuskers', ' Tar Heels', ' Hurricanes',
        ' Cavaliers', ' Seminoles', ' Commodores', ' Revolutionaries', ' Patriots',
        ' Spiders', ' Hawks', ' Fighting Irish', ' Golden Eagles', ' Badgers',
        ' Fighting Illini', ' Leathernecks', ' Utes', ' Blue Devils', ' Cyclones',
        ' Horned Frogs', ' Razorbacks', ' Sun Devils', ' Falcons', ' Rebels',
        ' Crimson Tide', ' Gators', ' Hokies', ' Mountain Hawks', ' Pirates',
        ' Orange', ' Greyhounds', ' Leopards', ' Rockets', ' Broncos', ' Keydets',
        ' Terriers', ' Mocs', ' Buccaneers', ' Ospreys', ' Dolphins', ' Hatters',
        ' Governors', ' Royals', ' Gamecocks', ' Miners', ' Thundering Herd',
        ' Monarchs', ' Buffaloes', ' Bobcats', ' Warhawks', ' Colonels', ' Bisons',
        ' Bluejays', ' Blue Demons', ' Demon Deacons', ' Yellow Jackets', ' Cardinal',
        ' Flames', ' Pilots', ' Toreros', ' Redhawks', ' Gaels', ' Waves', ' Lobos',
        ' Lopes', ' Catamounts', ' Explorers', ' Raiders', ' Crusaders', ' Black Knights',
        ' Golden Flashes', ' Coyotes', ' Golden Bears', ' Griffins', ' Golden Griffins'
    ]

    for mascot in mascots:
        if name.endswith(mascot):
            name = name[:-len(mascot)].strip()
            break

    # Normalize common variations
    name = name.replace('State', 'St.').replace('St ', 'St. ')
    name = name.replace('&', 'and')

    return name.lower().strip()


def find_kenpom_match(espn_team, kenpom_df):
    """Find matching team in KenPom data using multiple strategies."""

    # Strategy 1: Exact hardcoded mappings for known problem cases
    exact_mappings = {
        'Miami': 'Miami FL',
        'Miami Hurricanes': 'Miami FL',
        'IU Indianapolis': 'Indianapolis',
        'IU Indianapolis Jaguars': 'Indianapolis',
        'San José State': 'San Jose St.',
        'San Jose State': 'San Jose St.',
        'USC': 'Southern California',
        'USC Trojans': 'Southern California',
        'UCF': 'Central Florida',
        'UAB': 'Alabama Birmingham',
        'VCU': 'Virginia Commonwealth',
        'UConn': 'Connecticut',
        'UNC Greensboro': 'UNC Greensboro',
        'UTSA': 'UT San Antonio',
        'UTEP': 'UTEP',
        'UL Monroe': 'Louisiana Monroe',
        'App State': 'Appalachian St.',
        'Ole Miss': 'Mississippi',
        'Alabama Crimson Tide': 'Alabama',
        'The Citadel': 'Citadel',
        'American University': 'American',
        'Loyola Maryland': 'Loyola MD',
        'VMI': 'VMI',
        'Penn State': 'Penn St.',
        'NC State': 'N.C. State',
        'Saint Joseph\'s': 'Saint Joseph\'s',
        'St. John\'s': 'St. John\'s',
    }

    # Check exact mappings first
    for key, value in exact_mappings.items():
        if key.lower() in espn_team.lower():
            for idx, row in kenpom_df.iterrows():
                if value.lower() == str(row['Team']).lower().strip():
                    return row

    # Strategy 2: Clean both names and try exact match
    espn_clean = clean_team_name_simple(espn_team)

    for idx, row in kenpom_df.iterrows():
        kenpom_clean = clean_team_name_simple(str(row['Team']))

        if espn_clean == kenpom_clean:
            return row

    # Strategy 3: Check if ESPN name contains KenPom name or vice versa
    for idx, row in kenpom_df.iterrows():
        kenpom_name = str(row['Team']).lower().strip()
        espn_lower = espn_team.lower()

        # Split into words and check for substantial overlap
        kenpom_words = set(kenpom_name.split())
        espn_words = set(espn_lower.split())

        # Remove common words
        common_words = {'state', 'st.', 'st', 'university', 'of', 'the', 'and'}
        kenpom_words = kenpom_words - common_words
        espn_words = espn_words - common_words

        # If significant word overlap, consider it a match
        if kenpom_words and espn_words:
            overlap = len(kenpom_words & espn_words)
            if overlap >= min(len(kenpom_words), len(espn_words)) * 0.7:
                return row

    # Strategy 4: Check first word match (handles most state schools)
    espn_first = espn_clean.split()[0] if espn_clean else ""
    if len(espn_first) > 3:  # Avoid matching short words
        for idx, row in kenpom_df.iterrows():
            kenpom_clean = clean_team_name_simple(str(row['Team']))
            kenpom_first = kenpom_clean.split()[0] if kenpom_clean else ""

            if espn_first == kenpom_first and len(espn_first) > 4:
                return row

    return None


def get_team_data(team_name, kenpom_df, hca_df, barttorvik_df):
    """Get all stats for a team including DYNAMIC HCA."""

    # Find in KenPom using smart matching
    kenpom_row = find_kenpom_match(team_name, kenpom_df)

    if kenpom_row is None:
        return None

    # Get the actual KenPom team name for matching in other datasets
    kenpom_team_name = str(kenpom_row['Team']).strip()

    # Get DYNAMIC HCA from hca_rankings.csv
    hca = 3.5  # Default fallback
    for idx, row in hca_df.iterrows():
        if str(row['Team']).strip().lower() == kenpom_team_name.lower():
            hca = float(row['HCA'])
            break

    # Get shot data with defense
    shot_data = None
    for idx, row in barttorvik_df.iterrows():
        if str(row['team']).strip().lower() == kenpom_team_name.lower():
            shot_data = {
                'rim_rate': float(row['rim_rate']),
                'mid_rate': float(row['mid_rate']),
                'three_rate': float(row['three_rate']),
                'rim_fg_def': float(row['rim_fg_def']),
                'mid_fg_def': float(row['mid_fg_def']),
                'three_fg_def': float(row['three_fg_def'])
            }
            break

    return {
        'team': team_name,
        'adj_oe': float(kenpom_row['ORtg']),
        'adj_de': float(kenpom_row['DRtg']),
        'adj_tempo': float(kenpom_row['AdjT']),
        'hca': hca,
        'shot_data': shot_data
    }


def calc_shot_quality_with_defense(off_shot_data, def_shot_data):
    """Calculate shot quality edge with defensive matchup."""
    LEAGUE_RIM_FG = 62.0
    LEAGUE_MID_FG = 38.0
    LEAGUE_THREE_FG = 34.5

    if off_shot_data is None:
        base_value = (0.45 * 2.0) + (0.20 * 2.0) + (0.35 * 3.0)
        return 0.0105 * base_value

    rim_rate = off_shot_data['rim_rate']
    mid_rate = off_shot_data['mid_rate']
    three_rate = off_shot_data['three_rate']

    if def_shot_data is not None and 'rim_fg_def' in def_shot_data:
        rim_fg_def = def_shot_data['rim_fg_def']
        mid_fg_def = def_shot_data['mid_fg_def']
        three_fg_def = def_shot_data['three_fg_def']

        rim_def_factor = rim_fg_def / LEAGUE_RIM_FG
        mid_def_factor = mid_fg_def / LEAGUE_MID_FG
        three_def_factor = three_fg_def / LEAGUE_THREE_FG

        rim_value = rim_rate * rim_def_factor * 2.0
        mid_value = mid_rate * mid_def_factor * 2.0
        three_value = three_rate * three_def_factor * 3.0

        total_value = rim_value + mid_value + three_value
    else:
        total_value = (rim_rate * 2.0) + (mid_rate * 2.0) + (three_rate * 3.0)

    return 0.0105 * total_value


def predict_game(away_team, home_team, kenpom_df, hca_df, barttorvik_df):
    """
    Predict game using KenPom efficiency + defensive shot quality + DYNAMIC HCA.

    Model specifications:
    - Tempo: 52/48 weighting (52% fast, 48% slow)
    - Defense drag: 0.98
    - Calibration: 0.96
    - Shot quality: Minor adjustment (NOT multiplied by 100)
    - Dynamic HCA from hca_rankings.csv
    """
    away = get_team_data(away_team, kenpom_df, hca_df, barttorvik_df)
    home = get_team_data(home_team, kenpom_df, hca_df, barttorvik_df)

    if not away or not home:
        return None

    LEAGUE_AVG = 108.5

    # 1. TEMPO CALCULATION (Original Spec: 52% fast, 48% slow)
    fast = max(away['adj_tempo'], home['adj_tempo'])
    slow = min(away['adj_tempo'], home['adj_tempo'])
    possessions = (0.52 * fast) + (0.48 * slow)

    # 2. EFFICIENCY WITH DEFENSIVE DRAG
    DEFENSIVE_DRAG = 0.98
    away_eff = ((away['adj_oe'] * home['adj_de']) / LEAGUE_AVG) * DEFENSIVE_DRAG
    home_eff = ((home['adj_oe'] * away['adj_de']) / LEAGUE_AVG) * DEFENSIVE_DRAG

    # 3. SHOT QUALITY WITH DEFENSIVE MATCHUPS (MINOR ADJUSTMENT)
    away_sq = calc_shot_quality_with_defense(away['shot_data'], home['shot_data'])
    home_sq = calc_shot_quality_with_defense(home['shot_data'], away['shot_data'])

    # CRITICAL FIX: Do NOT multiply by 100
    # Shot quality is already in the right scale (0.5-2 point adjustment)
    away_eff_adj = away_eff + away_sq
    home_eff_adj = home_eff + home_sq

    # 4. CALIBRATION
    CALIBRATION = 0.96

    # Calculate final scores with DYNAMIC HCA
    away_score = (possessions * away_eff_adj) / 100.0 * CALIBRATION
    home_score = ((possessions * home_eff_adj) / 100.0 * CALIBRATION) + home['hca']

    spread = home_score - away_score
    if spread > 0:
        spread_display = f"{home_team} -{abs(spread):.1f}"
    else:
        spread_display = f"{away_team} -{abs(spread):.1f}"

    return {
        'away_team': away_team,
        'home_team': home_team,
        'away_score': round(away_score, 1),
        'home_score': round(home_score, 1),
        'spread': round(spread, 1),
        'spread_display': spread_display,
        'total': round(away_score + home_score, 1),
        'possessions': round(possessions, 1),
        'hca': round(home['hca'], 1)
    }


def predict_all_games(games_df, kenpom_df, hca_df, barttorvik_df, games_date):
    """Generate predictions for all games."""
    print("\n" + "=" * 60)
    print("GENERATING PREDICTIONS")
    print("=" * 60)

    predictions = []
    failed = []

    for idx, game in games_df.iterrows():
        away = game['away_team']
        home = game['home_team']

        print(f"\n{idx + 1}. {away} @ {home}")

        pred = predict_game(away, home, kenpom_df, hca_df, barttorvik_df)

        if pred:
            predictions.append(pred)
            print(f"   {away} {pred['away_score']} - {pred['home_score']} {home}")
            print(f"   Spread: {pred['spread_display']} | Total: {pred['total']:.1f}")
            print(f"   HCA: {pred['hca']:.1f}")
        else:
            failed.append(f"{away} @ {home}")
            print(f"   ✗ Failed (team not in D1 KenPom data)")

    if predictions:
        df = pd.DataFrame(predictions)
        output_file = f'predictions_{games_date}.csv'
        df.to_csv(output_file, index=False)

        print("\n" + "=" * 60)
        print(f"✓ Successfully predicted {len(predictions)}/{len(games_df)} games")
        if failed:
            print(f"✗ Failed: {len(failed)} games (non-D1 teams)")
            for game in failed:
                print(f"   - {game}")
        print(f"✓ Saved to {output_file}")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("COLLEGE BASKETBALL BETTING MODEL")
    print("KenPom + BartTorvik (Shot Quality as Minor Adjustment)")
    print("=" * 60)

    kenpom_df, hca_df, barttorvik_df, games_df, games_date = load_all_data()

    if all(v is not None for v in [kenpom_df, hca_df, barttorvik_df, games_df, games_date]):
        predict_all_games(games_df, kenpom_df, hca_df, barttorvik_df, games_date)