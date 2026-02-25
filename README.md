# CBB Predictive Analytics Engine

This is a Python-based system I built to find value in college basketball betting lines. It uses team efficiency metrics and tempo-adjusted stats to calculate what a "fair" spread should be for any D1 matchup, then compares that to live Vegas lines to find an edge.

## How it works
The engine pulls advanced metrics (AdjO, AdjD, and Tempo) for all 360+ Division I teams. It runs a calculation that accounts for things like home-court advantage and how a team's pace affects the total number of possessions in a game.

- **Data Sync:** It uses fuzzy matching to handle the fact that every sports site spells team names differently (e.g., "NC State" vs "North Carolina St").
- **Edge Detection:** The script flags any game where my model's line differs from the Vegas spread by 3 points or more.
- **The Process:** It’s currently built to run as a local CLI tool in PyCharm, outputting a CSV of the day's best value plays.

## Current Performance
I've been tracking this live during the 2025-26 season. As of today:
- **Record:** 30-20 (60.0% win rate) over a 50-game sample.
- This success rate is based on sticking to games where the model identifies a clear statistical edge rather than betting every matchup on the board.

## Technical Stack
- **Python 3.x**
- **Pandas/NumPy** for the data crunching.
- **BeautifulSoup** for scraping the latest efficiency numbers.
- Developed and tested in **PyCharm**.

## The Roadmap
The biggest challenge right now is that the model is "blind" to injuries. If a star player is out, the efficiency metrics are skewed. My next step is building a scraper for daily injury reports to automatically "punish" a team's rating when they're shorthanded. I'm also looking into moving from a static regression to a Random Forest model to see if it catches late-season variance better.

---
**Tony Calloway** *Computer Science Senior, East Carolina University*