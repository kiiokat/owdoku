# OWdoku

A free daily grid puzzle for Overwatch esports fans, in the style of
[Puckdoku](https://www.puckdoku.com/). Each day there's a 3x3 grid: fill each square with a
pro player who fits both its row and its column, such as a player who played for Team Liquid
and competed in OWCS 2024.

**Play:** https://owdoku.pages.dev (test address until the game launches on its own domain)

OWdoku is a non-commercial fan project with no ads or paid features.

## Features

- **A weekly plan:** Monday to Thursday are OWCS days (current players), Friday is Contenders Day,
  Saturday is OWL Day and Sunday is APEX Day. Contenders and APEX days don't move your rank.
- **Leagues covered:** OGN APEX (2016–2018), the Overwatch League and Contenders (2018–2023),
  OWCS (2024 onward) and the Overwatch World Cup.
- **Categories:** teams, roles, top heroes, nationalities, OWL seasons and champions, OWCS years,
  regions, World Finals and international champions, and World Cup players and champions.
- **Rank, streaks and 41 achievements**, all earned from the game's own data.
- **Pick percentages and rarity scores** once 50 people have played a day's grid.
- **Practice Range:** unlimited grids for any of the four leagues; nothing counts.
- **Archive** of past grids behind the calendar button.
- **Streamer vs Chat** (desktop): open `owdoku.pages.dev/#streamer` or type `streamer` on the page.
  The streamer races their Twitch chat for the grid. Chat is read anonymously; no login.
- Forgiving search: ignores case and accents, knows players' old names.

## How it works

The whole game is one page, `index.html`: game logic, player data, flags and team icons are all
inside it. To run it locally, serve the folder with any static web server
(for example `python -m http.server`) and open it in a browser.

- Daily grids are generated from the date, so everyone gets the same puzzle. `FIXED_GRIDS` pins a
  date to an exact grid when a played daily needs protecting from data changes.
- `ROTATION_START` holds the game at puzzle #1 until it's set to a date (`"YYYY-MM-DD"`); from that
  day a new grid appears each midnight.
- Progress, stats and settings stay in the player's browser. The only thing sent to a server is a
  finished daily game's answers, anonymously, for pick percentages; see [`worker/`](worker/README.md).
- Testing tools: type `owdev` on the page or add `#dev` to the address.

The site is served by Cloudflare Pages from the `gh-pages` branch, which also holds the hero
portraits (see [`heroes/`](heroes/README.md)). The stats server in `worker/` deploys from `main`.

## Refreshing the player data

Run this after each OWCS stage, or whenever rosters have moved.

1. **Fetch from Liquipedia.** You need a Liquipedia API key (never commit it):
   ```
   python3 tools/fetch-liquipedia.py            # every dataset
   python3 tools/fetch-liquipedia.py regional   # or just one
   ```
   The key is read from the `LIQUIPEDIA_API_KEY` environment variable, or asked for (hidden).
   Files land in `liquipedia_data/`: `players`, `squadplayers`, `placements`, `contenders`,
   `regional` and `worldcup`.
2. **Rebuild the game data** from those files. The rebuild scripts were written to run in a
   Claude session: they read the Liquipedia files from `/home/claude/lpdata/` and the game from
   `/home/claude/owdoku.html`. The simplest refresh is to start a session, attach the new files,
   and ask for a rebuild using this list, in this order:
   - `tools/lpmatch.py`, `tools/lppatch.py`: match Liquipedia players to the game; nationalities, old names
   - `tools/owcs_build.py`, `tools/apex_build.py`, `tools/cont_build.py`: OWCS, APEX and Contenders rosters
   - `tools/xcheck.py`, then `tools/xapply.py`: cross-check OWL rosters, Liquipedia wins
   - `tools/owcs_extra.py index.html`: OWCS years, regions, World Finals, international and World Cup titles
   - `tools/check-badges.py`: flags any team icon that clashes with its badge colour
3. **Regenerate the stats server's player list** (`worker/src/players.js`) so new names are accepted.
4. **Check before publishing:** open the page with `#dev`, try the 🎲 and 🏛️ buttons, and make sure
   today's grid hasn't changed. If it has, pin it in `FIXED_GRIDS`.

## Credits

- **Player data:** official Overwatch League Stats Lab match records, and
  [Liquipedia](https://liquipedia.net/overwatch/) (rosters, nationalities, old names, OWCS, APEX,
  Contenders and World Cup results), licensed [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
- **Hero portraits:** [overwatch.blizzard.com](https://overwatch.blizzard.com/en-us/heroes/),
  not included in this repository. Overwatch and all related characters and artwork are
  © and ™ Blizzard Entertainment, Inc.
- **Flags:** [flag-icons](https://github.com/lipis/flag-icons) (MIT)
- **Team icons:** [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) by Microsoft (MIT).
  No official team logos are used.
- **Fonts:** Bricolage Grotesque, Geist, Geist Mono and Saira Extra Condensed via
  [Google Fonts](https://fonts.google.com/) (SIL Open Font License)
- **Logo and sounds:** original to OWdoku. Sound effects are generated in the browser; no audio files.

OWdoku is not affiliated with or endorsed by Blizzard Entertainment, the Overwatch League,
Twitch or Liquipedia.
