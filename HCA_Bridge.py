import os
import pandas as pd
from dotenv import load_dotenv
from kenpompy.utils import login
from kenpompy import misc

load_dotenv()


def fetch_hca_data():
    print("Connecting to KenPom for Home Court Advantage data...")
    try:
        browser = login(os.getenv('KENPOM_EMAIL'), os.getenv('KENPOM_PASSWORD'))

        print("Logged in successfully!")
        print("Pulling HCA values...")

        hca_df = misc.get_hca(browser)

        hca_df.to_csv('hca_rankings.csv', index=False)

        print("\n--- SUCCESS! ---")
        print(f"Saved {len(hca_df)} teams' HCA data to 'hca_rankings.csv'")

        print("\nSample HCA data:")
        print(hca_df.head(10))

        browser.close()
        return hca_df

    except Exception as e:
        print(f"HCA Sync Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure KENPOM_EMAIL and KENPOM_PASSWORD are in .env file")
        print("2. Verify your KenPom subscription is active")
        print("3. Try: pip install kenpompy")
        return None


if __name__ == "__main__":
    fetch_hca_data()