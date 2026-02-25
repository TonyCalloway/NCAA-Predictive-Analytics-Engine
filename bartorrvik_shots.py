import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def scrape_barttorvik_shots_selenium():
    """
    Scrape BartTorvik shot distribution AND defensive efficiency.
    """
    print("=" * 60)
    print("BARTTORVIK SHOT DISTRIBUTION SCRAPER (WITH DEFENSE)")
    print("=" * 60)

    url = "https://barttorvik.com/teampbp.php?year=2026&sort=1"

    print(f"\nTarget URL: {url}")
    print("\nLaunching Chrome...")

    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None

    try:
        driver = webdriver.Chrome(options=chrome_options)

        print(f"\n1. Navigating to page...")
        driver.get(url)

        print("2. Waiting for page to load...")
        time.sleep(8)

        # Get page source
        page_source = driver.page_source

        # Save HTML
        with open('barttorvik_teampbp.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("3. ✓ Saved HTML")

        driver.quit()

        # Parse with BeautifulSoup
        print("\n4. Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the table
        table = soup.find('table')

        if not table:
            print("ERROR: No table found!")
            return None

        # Extract data from table
        data = []

        # Get all rows
        rows = table.find_all('tr')
        print(f"   Found {len(rows)} rows")

        # Parse each row
        for row in rows:
            cells = row.find_all('td')

            if len(cells) < 10:  # Skip header/short rows
                continue

            # Extract text from each cell
            row_data = []
            for cell in cells:
                text = cell.get_text(strip=True)
                row_data.append(text)

            if row_data and len(row_data) > 5:
                data.append(row_data)

        print(f"   Extracted {len(data)} data rows")

        if len(data) == 0:
            print("ERROR: No data extracted!")
            return None

        df = pd.DataFrame(data)

        print(f"\n5. Created DataFrame: {df.shape[0]} rows × {df.shape[1]} columns")

        # Save raw
        df.to_csv('barttorvik_teampbp_raw.csv', index=False, header=False)
        print("   ✓ Saved to barttorvik_teampbp_raw.csv")

        print("\nFirst row (for debugging):")
        print(df.iloc[0].tolist()[:15])

        # Process the data
        return process_raw_data(df)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

        if driver:
            try:
                driver.quit()
            except:
                pass

        return None


def process_raw_data(df):
    """
    Process the raw scraped data into shot distribution AND defensive stats.

    BartTorvik columns (per shot type):
    - FG% (Offense)
    - SHARE (Offense)
    - FG% (Defense)
    - SHARE (Defense)
    """
    print("\n" + "=" * 60)
    print("PROCESSING SHOT DISTRIBUTION + DEFENSE")
    print("=" * 60)

    print(f"\nAnalyzing {df.shape[1]} columns...")

    # Team name is in column 1
    team_col = 1

    print(f"\nFirst row data (columns 0-14):")
    first_row = df.iloc[0].tolist()
    for i, val in enumerate(first_row[:15]):
        print(f"   Col {i:2d}: {val}")

    print("\n" + "=" * 60)
    print("COLUMN IDENTIFICATION")
    print("=" * 60)

    print("\nBased on the BartTorvik table structure:")
    print("Each shot type has 4 columns: FG%(Off), SHARE(Off), FG%(Def), SHARE(Def)")
    print("\nWe need to identify:")
    print("  OFFENSE columns:")
    print("    1. Dunk FG% (Offense)")
    print("    2. Dunk SHARE (Offense)")
    print("    3. Close Two FG% (Offense)")
    print("    4. Close Two SHARE (Offense)")
    print("    5. Farther Two FG% (Offense)")
    print("    6. Farther Two SHARE (Offense)")
    print("    7. Three FG% (Offense)")
    print("    8. Three SHARE (Offense)")
    print("\n  DEFENSE columns:")
    print("    9. Dunk FG% (Defense)")
    print("    10. Close Two FG% (Defense)")
    print("    11. Farther Two FG% (Defense)")
    print("    12. Three FG% (Defense)")

    print("\n" + "=" * 60)
    print("PREVIOUS SHARE COLUMNS: 4,9,14,19")
    print("=" * 60)

    print("\nBased on the pattern, columns should be:")
    print("  OFFENSE FG%:    3, 8, 13, 18")
    print("  OFFENSE SHARE:  4, 9, 14, 19 (confirmed working)")
    print("  DEFENSE FG%:    5, 10, 15, 20")
    print("  DEFENSE SHARE:  7, 12, 17, 22")

    print("\nVerifying with first row (Purdue):")
    print(f"  Dunk FG% (Off):    Col 3  = {df.iloc[0, 3]}")
    print(f"  Dunk SHARE (Off):  Col 4  = {df.iloc[0, 4]}")
    print(f"  Dunk FG% (Def):    Col 5  = {df.iloc[0, 5]}")
    print(f"  Close FG% (Off):   Col 8  = {df.iloc[0, 8]}")
    print(f"  Close SHARE (Off): Col 9  = {df.iloc[0, 9]}")
    print(f"  Close FG% (Def):   Col 10 = {df.iloc[0, 10]}")

    confirm = input("\nDoes this look correct? (y/n): ").strip().lower()

    if confirm != 'y':
        print("\nPlease manually identify the columns.")
        print("Check barttorvik_teampbp_raw.csv")
        return None

    # Column assignments
    # OFFENSE
    dunk_fg_off = 3
    dunk_share_off = 4
    close_fg_off = 8
    close_share_off = 9
    far_fg_off = 13
    far_share_off = 14
    three_fg_off = 18
    three_share_off = 19

    # DEFENSE
    dunk_fg_def = 5
    close_fg_def = 10
    far_fg_def = 15
    three_fg_def = 20

    # Extract the data
    result = pd.DataFrame()
    result['team'] = df.iloc[:, team_col]

    # OFFENSE - Shot Distribution (SHARE)
    result['dunk_share_off'] = pd.to_numeric(df.iloc[:, dunk_share_off], errors='coerce')
    result['close_share_off'] = pd.to_numeric(df.iloc[:, close_share_off], errors='coerce')
    result['far_share_off'] = pd.to_numeric(df.iloc[:, far_share_off], errors='coerce')
    result['three_share_off'] = pd.to_numeric(df.iloc[:, three_share_off], errors='coerce')

    # OFFENSE - Field Goal % (efficiency at each shot type)
    result['dunk_fg_off'] = pd.to_numeric(df.iloc[:, dunk_fg_off], errors='coerce')
    result['close_fg_off'] = pd.to_numeric(df.iloc[:, close_fg_off], errors='coerce')
    result['far_fg_off'] = pd.to_numeric(df.iloc[:, far_fg_off], errors='coerce')
    result['three_fg_off'] = pd.to_numeric(df.iloc[:, three_fg_off], errors='coerce')

    # DEFENSE - Field Goal % allowed (opponent's efficiency at each shot type)
    result['dunk_fg_def'] = pd.to_numeric(df.iloc[:, dunk_fg_def], errors='coerce')
    result['close_fg_def'] = pd.to_numeric(df.iloc[:, close_fg_def], errors='coerce')
    result['far_fg_def'] = pd.to_numeric(df.iloc[:, far_fg_def], errors='coerce')
    result['three_fg_def'] = pd.to_numeric(df.iloc[:, three_fg_def], errors='coerce')

    # Calculate aggregate rates for model compatibility
    result['rim_rate'] = (result['dunk_share_off'] + result['close_share_off']) / 100.0
    result['mid_rate'] = result['far_share_off'] / 100.0
    result['three_rate'] = result['three_share_off'] / 100.0

    # Calculate weighted offensive efficiency at rim/mid/three
    result['rim_fg_off'] = (
                                   (result['dunk_share_off'] * result['dunk_fg_off']) +
                                   (result['close_share_off'] * result['close_fg_off'])
                           ) / (result['dunk_share_off'] + result['close_share_off'])

    result['mid_fg_off'] = result['far_fg_off']
    result['three_fg_off'] = result['three_fg_off']

    # Calculate weighted defensive efficiency at rim/mid/three
    result['rim_fg_def'] = (
                                   (result['dunk_share_off'] * result['dunk_fg_def']) +
                                   (result['close_share_off'] * result['close_fg_def'])
                           ) / (result['dunk_share_off'] + result['close_share_off'])

    result['mid_fg_def'] = result['far_fg_def']
    result['three_fg_def'] = result['three_fg_def']

    # Keep needed columns
    final_cols = [
        'team',
        'rim_rate', 'mid_rate', 'three_rate',
        'rim_fg_off', 'mid_fg_off', 'three_fg_off',
        'rim_fg_def', 'mid_fg_def', 'three_fg_def'
    ]

    result = result[final_cols].copy()
    result = result.dropna()
    result['team'] = result['team'].astype(str).str.strip()

    # Save
    result.to_csv('barttorvik_splits.csv', index=False)

    print(f"\n✓ SUCCESS! Saved {len(result)} teams to barttorvik_splits.csv")

    print("\nFirst 10 teams:")
    print(result.head(10).to_string(index=False))

    print("\nValidation:")
    print(f"   Average rim rate: {result['rim_rate'].mean():.1%}")
    print(f"   Average mid rate: {result['mid_rate'].mean():.1%}")
    print(f"   Average three rate: {result['three_rate'].mean():.1%}")
    print(f"\n   Average rim FG% (offense): {result['rim_fg_off'].mean():.1f}%")
    print(f"   Average mid FG% (offense): {result['mid_fg_off'].mean():.1f}%")
    print(f"   Average three FG% (offense): {result['three_fg_off'].mean():.1f}%")
    print(f"\n   Average rim FG% allowed (defense): {result['rim_fg_def'].mean():.1f}%")
    print(f"   Average mid FG% allowed (defense): {result['mid_fg_def'].mean():.1f}%")
    print(f"   Average three FG% allowed (defense): {result['three_fg_def'].mean():.1f}%")

    return result


if __name__ == "__main__":
    result = scrape_barttorvik_shots_selenium()

    if result is not None:
        print("\n" + "=" * 60)
        print("✓ COMPLETE!")
        print("=" * 60)
        print("\nYour model now has offensive AND defensive shot data!")