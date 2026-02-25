import requests
import pandas as pd
from datetime import datetime
import os
import glob
from dotenv import load_dotenv

try:
    from Main_Model import clean_team_name
except ImportError:
    def clean_team_name(name):
        if pd.isna(name): return ""
        name = str(name).lower().strip()
        fluff = ['highlanders', 'retrievers', 'catamounts', 'beacons', 'racers', 'penguins',
                 'titans', 'skyhawks', 'sharks', 'phoenix', 'blue hens', 'flames', 'tommies',
                 'chanticleers', 'vikings', 'redhawks', 'beavers', 'jackrabbits',
                 'wildcats', 'rainbow warriors', 'roadrunners', 'beach', 'university', 'st.', 'st']
        for f in fluff:
            name = name.replace(f, '')
        name = name.replace('state', '').replace('&', 'and').replace('-', ' ')
        return "".join(name.split())

load_dotenv()


def teams_match(model_name, api_name):
    return clean_team_name(model_name) == clean_team_name(api_name)


def load_predictions():
    prediction_files = glob.glob('predictions_*.csv')
    if not prediction_files:
        print("✗ ERROR: No prediction files found. Run Main_Model.py first.")
        return None
    latest_file = max(prediction_files, key=os.path.getmtime)
    print(f"✓ Loaded {latest_file}")
    return pd.read_csv(latest_file)


def fetch_odds(api_key):
    url = f'https://api.the-odds-api.com/v4/sports/basketball_ncaab/odds/'
    params = {'apiKey': api_key, 'regions': 'us', 'markets': 'spreads', 'oddsFormat': 'american'}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"✗ API ERROR: {e}")
        return None


def compare_predictions(predictions_df, odds_data):
    print("\n" + "=" * 60)
    print("      SPREAD VALUE PLAYS (THRESHOLD: 3.0 - 11.9 EDGE)")
    print("=" * 60)

    for _, pred in predictions_df.iterrows():
        match = next((g for g in odds_data if teams_match(pred['away_team'], g['away_team'])
                      and teams_match(pred['home_team'], g['home_team'])), None)

        if not match:
            continue

        try:
            book = match['bookmakers'][0]

            # --- SPREAD COMPARISON ONLY ---
            s_market = next((m for m in book['markets'] if m['key'] == 'spreads'), None)
            if s_market:
                v_home_spread = next((o['point'] for o in s_market['outcomes'] if o['name'] == match['home_team']), 0)
                v_line_aligned = v_home_spread * -1
                m_line = pred['spread']
                s_edge = abs(m_line - v_line_aligned)

                if 3.0 <= s_edge < 12.0:
                    side = pred['home_team'] if (m_line > v_line_aligned) else pred['away_team']
                    print(f"🎯 SPREAD: {pred['away_team']} @ {pred['home_team']}")
                    print(f"   Model: {m_line:+.1f} | Vegas: {v_line_aligned:+.1f} | Edge: {s_edge:.1f}")
                    print(f"   👉 RECOMMENDATION: {side}")
                    print("-" * 30)

        except (IndexError, KeyError, TypeError):
            continue


if __name__ == "__main__":
    api_key = os.getenv('ODDS_API_KEY')
    preds = load_predictions()
    odds = fetch_odds(api_key)
    if preds is not None and odds:
        compare_predictions(preds, odds)