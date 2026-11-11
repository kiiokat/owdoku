# Data pipeline

Builds the game's player list from official Overwatch League Stats Lab match data.

1. Put the Stats Lab player CSVs in `raw_data/`, one folder per season
   (`raw_data/phs_2018/*.csv` through `raw_data/phs_2023/*.csv`).
   Archived copies: [rd11490/owl_work](https://github.com/rd11490/owl_work) (2018–2021),
   [Kaggle](https://www.kaggle.com/datasets/sherrytp/overwatch-league-stats-lab) and the
   Internet Archive's copy of the Stats Lab page (2022, 2023).
2. `python build_players.py` reads every match record and writes `players_full.json`:
   each player's OWL teams, seasons, championships, hours played, roles (any role with
   at least 25% of their playtime) and most-played hero per role.
3. `node merge2.js` writes that list into `../index.html`, keeping the hand-checked
   names, roles and countries already in the game.

Notes:
- 2019 playtime is skipped when working out roles for players with enough other time,
  because GOATS-era compositions put many DPS players on Brigitte and Zarya.
- In the 2022 file, Philadelphia Fusion and Paris Eternal appear under their 2023 names;
  the script sorts them back by year.
- Contenders and Pro-Am teams in the 2023 file are left out.
