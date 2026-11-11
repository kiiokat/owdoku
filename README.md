# OWdoku

A free daily grid puzzle for Overwatch esports fans, in the style of
[Puckdoku](https://www.puckdoku.com/). Each day there's a 3x3 grid: fill each square with a
pro player who fits both its row and its column, such as a player who played for the
London Spitfire and won an Overwatch League title.

**Play:** https://owdoku.pages.dev (also at https://claude.ai/artifact/TnpPVyRojpdPJXhndMrAuy)

OWdoku is a non-commercial fan project with no ads or paid features.

## Features

- A new daily puzzle at midnight (local time), plus unlimited practice grids and an archive of past days
- Any player with recorded Overwatch League play from 2018 to 2023 counts as an answer
- Three strikes, then the remaining answers are revealed
- Stats, streaks and a shareable result
- After the daily puzzle: what share of players picked each answer, and a rarity score
- Player cards with the player's most-played hero, role and country

## How it works

The whole game is one page, `index.html`: game logic, player data, flags and team icons
are all inside it. To run it locally, serve the folder with any static web server
(for example `python -m http.server`) and open it in a browser.

- Daily grids are generated from the date, so everyone gets the same puzzle. Each square
  must have at least three well-known answers (15+ hours of OWL play), and each day
  avoids the categories used in the two previous puzzles.
- Progress, stats and settings are saved in the player's own browser. The only thing sent
  to a server is a finished daily game's answers, anonymously, for pick percentages; see
  [`worker/`](worker/README.md).
- Testing tools: type `owdev` on the page, tap "OWdoku" in the credits five times, or add
  `#dev` to the address.

Player data is built by the scripts in [`data-pipeline/`](data-pipeline/README.md).
Hero portraits are downloaded separately; see [`heroes/`](heroes/README.md).
The site at owdoku.pages.dev is served by Cloudflare Pages from the `gh-pages` branch, which includes the portraits.

## Planned

- Player data from [Liquipedia](https://liquipedia.net/overwatch/) (nationality, roles,
  full team histories, Contenders and OWCS), credited under CC-BY-SA 3.0

## Credits

- **Player data:** official Overwatch League Stats Lab match records
- **Hero portraits:** [overwatch.blizzard.com](https://overwatch.blizzard.com/en-us/heroes/),
  not included in this repository. Overwatch and all related characters and artwork are
  © and ™ Blizzard Entertainment, Inc.
- **Flags:** [flag-icons](https://github.com/lipis/flag-icons) (MIT)
- **Team icons:** [Fluent Emoji](https://github.com/microsoft/fluentui-emoji) by Microsoft (MIT).
  No official team logos are used.

OWdoku is not affiliated with or endorsed by Blizzard Entertainment, the Overwatch League,
or Liquipedia.
