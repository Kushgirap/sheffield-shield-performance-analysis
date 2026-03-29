# SA Sheffield Shield Performance Analysis 2025/26

Performance analysis of South Australia's Sheffield Shield 2025/26 season, built using ball-by-ball data from Cricsheet. Developed to support pre-final preparation for SACA's performance analysis team.

## Project Overview

This repository replicates the workflow of a professional cricket performance analyst — combining data processing, statistical analysis, and visual storytelling to produce actionable insights ahead of the Sheffield Shield Final.

The analysis covers SA's 9 matches across 5 key areas:
- Season results and match outcomes
- Batting performance and partnerships
- Bowling performance and dismissal patterns
- Player form and consistency
- Tactical patterns (batting position vs result, phase analysis)

## Repository Structure
```
├── data/
│   ├── processed/          # Processed CSV data
│   │   └── sa_2025_26.csv  # Ball-by-ball data for SA's 9 matches
│   └── Raw/                # Raw Cricsheet JSON files (gitignored)
├── dashboards/             # Tableau packaged workbooks
├── notebooks/              # Match review Jupyter notebooks
├── reports/                # PDF match reports
├── docs/                   # Methodology and assumptions
└── README.md
```

## Dashboards

Built in Tableau, covering:
1. **Season Overview** — results, top performers, batting position analysis
2. **Batting Performance** — innings scores, dismissal types, run progression, batter stats
3. **Bowling Performance** — bowler workload, dot ball %, wickets by phase

## Data Source

Ball-by-ball data sourced from [Cricsheet](https://cricsheet.org) — Sheffield Shield 2025/26 season.

## Tools Used

- Python (pandas) — data processing
- Tableau — dashboards and visualisation
- Jupyter Notebooks — match analysis


## Match Reports

Detailed post-match reports produced for individual SA fixtures:

| Match | Season | Report |
|-------|--------|--------|
| SA vs QLD | 2024/25 | `reports/SA_vs_QLD_review.pdf` |
| SA vs NSW | 2024/25 | `reports/Kush_Girap_SA_vs_NSW_report.pdf` |

Each report covers:
- Match summary and result context
- Batting innings breakdown
- Bowling spell analysis
- Key moments and tactical observations
- Player performance highlights