"""
Cricsheet JSON → CSV Converter
================================
Converts one or more Cricsheet Sheffield Shield JSON files into a single
flat ball-by-ball CSV, including all wicket, extras, and match-info columns.

USAGE
-----
# Single file:
    python cricsheet_to_csv.py --input path/to/match.json --output output.csv

# Entire folder (all .json files):
    python cricsheet_to_csv.py --input path/to/json_folder --output output.csv

# Filter to South Australia matches only (2025/26 season):
    python cricsheet_to_csv.py --input path/to/json_folder --output sa_2025_26.csv --team "South Australia" --season "2025/26"

REQUIREMENTS
------------
    pip install pandas  (only stdlib + pandas needed)
"""

import json
import os
import argparse
import pandas as pd
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_match_info(info: dict, match_id: str) -> dict:
    """Pull top-level match metadata from the 'info' block."""
    teams = info.get("teams", [])
    outcome = info.get("outcome", {})

    # Result string
    if "winner" in outcome:
        winner = outcome["winner"]
        by = outcome.get("by", {})
        by_str = ", ".join(f"{v} {k}" for k, v in by.items())
        result = f"{winner} won by {by_str}"
    elif "result" in outcome:
        result = outcome["result"]          # e.g. "draw", "tie"
        winner = None
    else:
        result = "unknown"
        winner = None

    toss = info.get("toss", {})

    return {
        "match_id":            match_id,
        "season":              info.get("season", ""),
        "event":               info.get("event", {}).get("name", ""),
        "match_number":        info.get("event", {}).get("match_number", ""),
        "dates":               ", ".join(info.get("dates", [])),
        "start_date":          info.get("dates", [None])[0],
        "venue":               info.get("venue", ""),
        "city":                info.get("city", ""),
        "team_1":              teams[0] if len(teams) > 0 else "",
        "team_2":              teams[1] if len(teams) > 1 else "",
        "toss_winner":         toss.get("winner", ""),
        "toss_decision":       toss.get("decision", ""),
        "result":              result,
        "winner":              winner or "",
        "player_of_match":     ", ".join(info.get("player_of_match", [])),
    }


def parse_deliveries(data: dict, match_id: str) -> list[dict]:
    """Flatten all innings → overs → deliveries into a list of row dicts."""
    info   = data["info"]
    meta   = extract_match_info(info, match_id)
    rows   = []

    for innings_idx, innings in enumerate(data.get("innings", []), start=1):
        batting_team  = innings.get("team", "")
        teams         = info.get("teams", [])
        bowling_team  = next((t for t in teams if t != batting_team), "")

        for over_block in innings.get("overs", []):
            over_num = over_block["over"]

            for ball_idx, delivery in enumerate(over_block.get("deliveries", []), start=1):

                # ── Runs ──────────────────────────────────────────────────
                runs        = delivery.get("runs", {})
                runs_batter = runs.get("batter", 0)
                runs_extras = runs.get("extras", 0)
                runs_total  = runs.get("total", 0)

                # ── Extras breakdown ──────────────────────────────────────
                extras_detail = delivery.get("extras", {})
                wides    = extras_detail.get("wides", 0)
                noballs  = extras_detail.get("noballs", 0)
                byes     = extras_detail.get("byes", 0)
                legbyes  = extras_detail.get("legbyes", 0)
                penalty  = extras_detail.get("penalty", 0)

                is_wide   = 1 if wides   else 0
                is_noball = 1 if noballs else 0

                # ── Wicket ────────────────────────────────────────────────
                wickets = delivery.get("wickets", [])
                # A delivery can theoretically have 2 wickets (rare run-out)
                # We capture the first wicket's details; flag multi-wicket balls
                is_wicket       = 1 if wickets else 0
                player_dismissed = ""
                dismissal_type   = ""
                wicket_bowler    = ""  # credited to current bowler
                fielder_1        = ""
                fielder_2        = ""

                if wickets:
                    w = wickets[0]
                    player_dismissed = w.get("player_out", "")
                    dismissal_type   = w.get("kind", "")
                    wicket_bowler    = delivery.get("bowler", "")
                    fielders         = w.get("fielders", [])
                    fielder_1        = fielders[0].get("name", "") if len(fielders) > 0 else ""
                    fielder_2        = fielders[1].get("name", "") if len(fielders) > 1 else ""

                    # For run-outs the wicket bowler may differ from the current bowler
                    # Cricsheet doesn't separate this, so we keep current bowler

                row = {
                    # Match info
                    **meta,
                    # Innings / over / ball
                    "innings":           innings_idx,
                    "batting_team":      batting_team,
                    "bowling_team":      bowling_team,
                    "over":              over_num,
                    "ball_in_over":      ball_idx,
                    # Players
                    "batter":            delivery.get("batter", ""),
                    "non_striker":       delivery.get("non_striker", ""),
                    "bowler":            delivery.get("bowler", ""),
                    # Runs
                    "runs_batter":       runs_batter,
                    "runs_extras":       runs_extras,
                    "runs_total":        runs_total,
                    # Extras detail
                    "wides":             wides,
                    "noballs":           noballs,
                    "byes":              byes,
                    "legbyes":           legbyes,
                    "penalty":           penalty,
                    "is_wide":           is_wide,
                    "is_noball":         is_noball,
                    # Wicket
                    "is_wicket":         is_wicket,
                    "player_dismissed":  player_dismissed,
                    "dismissal_type":    dismissal_type,
                    "wicket_bowler":     wicket_bowler,
                    "fielder_1":         fielder_1,
                    "fielder_2":         fielder_2,
                }
                rows.append(row)

    return rows


# ── Column order ──────────────────────────────────────────────────────────────

COLUMN_ORDER = [
    "match_id", "season", "event", "match_number", "start_date", "dates",
    "venue", "city", "team_1", "team_2",
    "toss_winner", "toss_decision", "result", "winner", "player_of_match",
    "innings", "batting_team", "bowling_team", "over", "ball_in_over",
    "batter", "non_striker", "bowler",
    "runs_batter", "runs_extras", "runs_total",
    "wides", "noballs", "byes", "legbyes", "penalty",
    "is_wide", "is_noball",
    "is_wicket", "player_dismissed", "dismissal_type", "wicket_bowler",
    "fielder_1", "fielder_2",
]


# ── Main ──────────────────────────────────────────────────────────────────────

def collect_json_files(input_path: str) -> list[Path]:
    p = Path(input_path)
    if p.is_file():
        return [p]
    elif p.is_dir():
        files = sorted(p.glob("*.json"))
        print(f"Found {len(files)} JSON files in {p}")
        return files
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")


def convert(input_path: str,
            output_path: str,
            team_filter: str = None,
            season_filter: str = None):

    json_files = collect_json_files(input_path)
    all_rows   = []
    skipped    = 0
    included   = 0

    for fp in json_files:
        try:
            data   = load_json(fp)
            info   = data.get("info", {})
            season = info.get("season", "")
            teams  = info.get("teams", [])

            # ── Optional filters ──────────────────────────────────────────
            if season_filter and season != season_filter:
                skipped += 1
                continue
            if team_filter and team_filter not in teams:
                skipped += 1
                continue

            match_id = fp.stem          # filename without .json as match ID
            rows     = parse_deliveries(data, match_id)
            all_rows.extend(rows)
            included += 1
            print(f"  ✓  {fp.name}  ({len(rows)} deliveries)  —  {' vs '.join(teams)}  [{season}]")

        except Exception as e:
            print(f"  ✗  {fp.name}  ERROR: {e}")

    print(f"\nIncluded: {included} matches  |  Skipped: {skipped} matches")

    if not all_rows:
        print("No rows to write — check your filters.")
        return

    df = pd.DataFrame(all_rows)

    # Reorder columns (keep any extra cols at the end)
    existing_ordered = [c for c in COLUMN_ORDER if c in df.columns]
    extra_cols       = [c for c in df.columns if c not in COLUMN_ORDER]
    df = df[existing_ordered + extra_cols]

    df.to_csv(output_path, index=False)
    print(f"\n✅  Saved {len(df):,} rows → {output_path}")
    print(f"   Columns: {list(df.columns)}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Cricsheet Sheffield Shield JSON files to CSV."
    )
    parser.add_argument(
        "--input",  required=True,
        help="Path to a single .json file OR a folder containing .json files"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output CSV file path (e.g. sa_2025_26.csv)"
    )
    parser.add_argument(
        "--team",   default=None,
        help='Filter to matches involving this team (e.g. "South Australia")'
    )
    parser.add_argument(
        "--season", default=None,
        help='Filter to a specific season (e.g. "2025/26")'
    )

    args = parser.parse_args()
    convert(args.input, args.output, args.team, args.season)
