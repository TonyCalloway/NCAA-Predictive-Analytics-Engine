import undetected_chromedriver as uc
import pandas as pd
import time
import os
import io


def fetch_premium_data():
    print("=" * 60)
    print("KENPOM DATA SCRAPER")
    print("=" * 60)

    print("\nLaunching browser...")

    save_path = r"C:\Users\tonyc\PycharmProjects\CBB_Betting_Model\kenpom_stats.csv"

    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=144)

    try:
        print("\n1. Opening KenPom...")
        driver.get("https://kenpom.com/index.php?y=2026")

        print("\n2. Please LOG IN manually in the browser")
        print("   Email: tonycalloway82@gmail.com")
        print("   Password: Steelerrb26")
        input("\n   Press ENTER after you've logged in...")

        print("\n3. Extracting table data...")
        source_code = driver.page_source

        # Parse HTML tables
        html_buffer = io.StringIO(source_code)
        tables = pd.read_html(html_buffer)

        if not tables:
            print("\n✗ ERROR: No tables found!")
            print("   Make sure you're logged in and on the ratings page.")
            driver.quit()
            return

        # Get the main ratings table (usually the largest)
        df = max(tables, key=lambda x: len(x))

        print(f"\n4. Found table with {len(df)} teams and {len(df.columns)} columns")

        # CRITICAL FIX: Handle multi-level column headers
        if isinstance(df.columns, pd.MultiIndex):
            print("\n5. Cleaning up multi-level headers...")

            # Get just the last level of column names
            df.columns = df.columns.get_level_values(-1)

            # Remove duplicate column names
            df = df.loc[:, ~df.columns.duplicated()]

        # Show what columns we have
        print("\n6. Columns in cleaned table:")
        for i, col in enumerate(df.columns[:15]):
            print(f"      {i:2d}. {col}")

        # Show first row as example
        print("\n7. First team data:")
        if len(df) > 0:
            first_team = df.iloc[0]
            for i in range(min(12, len(first_team))):
                print(f"      Column {i}: {df.columns[i]} = {first_team.iloc[i]}")

        # Save to CSV
        df.to_csv(save_path, index=False)

        if os.path.exists(save_path):
            print(f"\n✓ SUCCESS! Saved {len(df)} teams to:")
            print(f"   {save_path}")
        else:
            print("\n✗ File wasn't saved. Check folder permissions.")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)[:200]}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nClosing browser...")
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    fetch_premium_data()