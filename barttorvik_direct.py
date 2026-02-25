import pandas as pd
import requests


def download_barttorvik_csv():
    """
    Download BartTorvik data directly from their CSV export.
    This is the most reliable method.
    """
    print("=" * 60)
    print("DOWNLOADING BARTTORVIK CSV")
    print("=" * 60)

    # Direct CSV URL
    url = "https://barttorvik.com/2026_team_results.csv"

    print(f"\nDownloading from: {url}")

    try:
        df = pd.read_csv(url)
        print(f"✓ Downloaded {len(df)} teams")

        print("\nColumns available:")
        print(df.columns.tolist())

        # Extract what we need
        # Typical columns: team, adjoe, adjde, adj_t, 3PR (3-point rate)

        # Map to our needed columns
        result = df[['team', 'adjoe', 'adjde', 'adj_t']].copy()

        # Get 3-point rate
        if '3PR' in df.columns:
            result['three_rate'] = df['3PR'] / 100.0
        elif '3pr' in df.columns:
            result['three_rate'] = df['3pr'] / 100.0
        else:
            print("WARNING: Cannot find 3PR column")
            result['three_rate'] = 0.35  # Default

        # Calculate rim and mid rates
        result['rim_rate'] = (1.0 - result['three_rate']) * 0.70
        result['mid_rate'] = (1.0 - result['three_rate']) * 0.30

        # Rename adj_t to adjt
        result = result.rename(columns={'adj_t': 'adjt'})

        # Save
        result.to_csv('barttorvik_splits.csv', index=False)
        print(f"\n✓ Saved {len(result)} teams to barttorvik_splits.csv")

        print("\nSample:")
        print(result.head(10))

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        return None


if __name__ == "__main__":
    download_barttorvik_csv()