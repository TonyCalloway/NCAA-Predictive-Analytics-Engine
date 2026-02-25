import requests
import pandas as pd
from datetime import datetime, timedelta
import sys


def fetch_espn_schedule(date_str):
    """Fetch games from ESPN API for a specific date."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"

    params = {
        'limit': 500,
        'dates': date_str,
        'groups': '50'  # Division 1 only
    }

    print(f"Fetching games for {date_str} from ESPN API...")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return data.get('events', [])
    except requests.exceptions.RequestException as e:
        print(f"✗ ERROR fetching schedule: {e}")
        return None


def parse_games(events):
    """Parse ESPN API events into game data."""
    games = []

    for event in events:
        competition = event.get('competitions', [{}])[0]
        competitors = competition.get('competitors', [])

        if len(competitors) != 2:
            continue

        # Get teams
        away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
        home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)

        if not away_team or not home_team:
            continue

        away_name = away_team.get('team', {}).get('displayName', '')
        home_name = home_team.get('team', {}).get('displayName', '')

        games.append({
            'away_team': away_name,
            'home_team': home_name
        })

    return games


if __name__ == "__main__":
    print("=" * 60)
    print("ESPN SCHEDULE SCRAPER - TOMORROW'S GAMES")
    print("=" * 60)

    # Get TOMORROW's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')

    # Fetch games
    events = fetch_espn_schedule(tomorrow)

    if events is None:
        print("✗ Failed to fetch schedule")
        sys.exit(1)

    # Parse games
    games = parse_games(events)

    if not games:
        print(f"\n✗ No games found for tomorrow ({tomorrow})")
        sys.exit(1)

    print(f"\n✓ Found {len(games)} games for tomorrow!")

    # Display games
    for i, game in enumerate(games, 1):
        print(f"  {i}. {game['away_team']} @ {game['home_team']}")

    # Save to CSV
    df = pd.DataFrame(games)
    output_file = f'games_{tomorrow}.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to {output_file}")