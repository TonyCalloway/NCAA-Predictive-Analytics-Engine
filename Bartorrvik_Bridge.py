import pandas as pd


def fetch_barttorvik_splits():
    print("Connecting to Barttorvik for shot split data...")
    # This URL targets the 2026 'Team Stats Play-by-Play' results directly
    url = "https://barttorvik.com/2026_team_results.csv"

    try:
        # Pull the raw CSV data
        df = pd.read_csv(url)

        # We save the full file so your Logic Engine can pull the specific
        # shares for Rim, Midrange, and 3PT later.
        df.to_csv('barttorvik_splits.csv', index=False)
        print("\n--- SUCCESS! ---")
        print("Barttorvik shot splits saved as 'barttorvik_splits.csv'")

    except Exception as e:
        print(f"Error fetching Barttorvik data: {e}")


if __name__ == "__main__":
    fetch_barttorvik_splits()