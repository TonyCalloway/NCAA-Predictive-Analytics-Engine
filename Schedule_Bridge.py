import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_todays_slate(date=None):
    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    print(f"Fetching games for {date} from ESPN API...")

    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?limit=500&dates={date}&groups=50"

        print(f"API URL: {url}")

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Error: ESPN API returned status {response.status_code}")
            return []

        data = response.json()
        events = data.get('events', [])

        if not events:
            print(f"\nNo games found for {date}")
            return []

        print(f"\nFound {len(events)} Division 1 games!\n")

        games = []

        for event in events:
            competitions = event.get('competitions', [])
            if not competitions:
                continue

            competition = competitions[0]
            competitors = competition.get('competitors', [])

            if len(competitors) < 2:
                continue

            home_team = competitors[0].get('team', {}).get('displayName', 'Unknown')
            away_team = competitors[1].get('team', {}).get('displayName', 'Unknown')

            game_date = event.get('date', '')
            game_status = event.get('status', {}).get('type', {}).get('description', '')
            venue = competition.get('venue', {}).get('fullName', 'Unknown Venue')

            home_score = competitors[0].get('score', '')
            away_score = competitors[1].get('score', '')

            games.append({
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'game_time': game_date,
                'status': game_status,
                'venue': venue
            })

        scheduled = [g for g in games if 'Scheduled' in g['status'] or 'Pre' in g['status']]
        in_progress = [g for g in games if 'In Progress' in g['status'] or 'Halftime' in g['status']]
        final = [g for g in games if 'Final' in g['status']]

        if scheduled:
            print(f"SCHEDULED GAMES ({len(scheduled)}):")
            for i, g in enumerate(scheduled, 1):
                print(f"  {i}. {g['away_team']} @ {g['home_team']}")

        if in_progress:
            print(f"\nIN PROGRESS ({len(in_progress)}):")
            for i, g in enumerate(in_progress, 1):
                print(f"  {i}. {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']}")

        if final:
            print(f"\nFINAL ({len(final)}):")
            for i, g in enumerate(final[:5], 1):
                print(f"  {i}. {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']}")
            if len(final) > 5:
                print(f"  ... and {len(final) - 5} more")

        df = pd.DataFrame(games)
        output_file = f'games_{date}.csv'
        df.to_csv(output_file, index=False)

        print(f"\nSUCCESS! Saved {len(games)} games to {output_file}")

        game_tuples = [(g['away_team'], g['home_team']) for g in games]
        return game_tuples

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("ESPN COLLEGE BASKETBALL SCHEDULE SCRAPER")
    print("=" * 60)

    today = datetime.now().strftime('%Y%m%d')
    games_today = fetch_todays_slate(today)

    if not games_today or len(games_today) < 5:
        print("\n" + "=" * 60)
        print("Not many games today. Trying tomorrow...")
        print("=" * 60)

        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
        games_tomorrow = fetch_todays_slate(tomorrow)