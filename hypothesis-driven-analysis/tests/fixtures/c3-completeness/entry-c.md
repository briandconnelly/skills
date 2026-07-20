## Data Validity

- Source completeness semantics: S2 (activity.csv) — an absent row means the incident had not closed as of 2026-06-22T23:59Z (this is the export's stated contract per PROBLEM.md: "activity.csv contains the recorded resolution activity as of the extract"); it does not mean the event is absent or unrecorded-but-happened. The still-open incidents have been open 8 to 17 days as of the extract (all past the stated 7-day maturation floor), so "not yet matured" does not explain the gap — these are incidents that have had enough time to close and have not.
