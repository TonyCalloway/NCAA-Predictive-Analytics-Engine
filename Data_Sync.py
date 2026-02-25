import pandas as pd
import webbrowser


def get_pasted_data(prompt):
    print(f"\n--- {prompt} ---")
    print("1. Highlight the data starting from Rank 1 down to the bottom.")
    print("2. Paste it here, type 'DONE' on a new line, and hit Enter.")
    lines = []
    while True:
        try:
            line = input().strip()
            if line.upper() == "DONE": break
            if line: lines.append(line)
        except EOFError:
            break
    return lines


def sync_data():
    webbrowser.open("https://barttorvik.com/2026teamstats.php")
    eff_lines = get_pasted_data("PASTE EFFICIENCY DATA")

    webbrowser.open("https://barttorvik.com/2026teamstats.php?pbp=1")
    shot_lines = get_pasted_data("PASTE SHOT DATA")

    eff_data = []
    for line in eff_lines:
        parts = line.split()
        # Find all decimal numbers (e.g., 110.5, 95.2, 70.1)
        decimals = [p for p in parts if '.' in p and p.replace('.', '', 1).isdigit()]

        # In the Efficiency table, the first 3 decimals are always AdjOE, AdjDE, AdjT
        if len(decimals) >= 3:
            # We assume the team name is the part immediately after the Rank (parts[0])
            # We clean it to help with the merge
            team_name = parts[1].lower()
            eff_data.append({
                'team': team_name,
                'adjoe': decimals[0],
                'adjde': decimals[1],
                'adjt': decimals[2]
            })

    shot_data = []
    for line in shot_lines:
        parts = line.split()
        decimals = [p for p in parts if '.' in p and p.replace('.', '', 1).isdigit()]

        # In the Shot Data table, the decimals we need start at index 1
        if len(decimals) >= 4:
            team_name = parts[1].lower()
            shot_data.append({
                'team': team_name,
                'rim_rate': decimals[1],
                'mid_rate': decimals[2],
                'three_rate': decimals[3]
            })

    eff_df = pd.DataFrame(eff_data)
    shot_df = pd.DataFrame(shot_data)

    if eff_df.empty:
        print(f"\nSTILL FAILING: Found 0 efficiency teams. Please paste the first 3 lines of your paste here!")
        return

    # Merge and Scale
    final_df = pd.merge(eff_df, shot_df, on='team')

    for col in ['adjoe', 'adjde', 'adjt', 'rim_rate', 'mid_rate', 'three_rate']:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
        if 'rate' in col:
            # Scale percentages to decimals to fix the 5.7 total error
            final_df[col] = final_df[col] / 100 if final_df[col].max() > 1 else final_df[col]

    final_df.to_csv('barttorvik_splits.csv', index=False)
    print(f"\nSUCCESS! {len(final_df)} teams matched. Your data is aligned.")


if __name__ == "__main__":
    sync_data()