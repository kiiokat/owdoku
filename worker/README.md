# Guess tracking server

A small [Cloudflare Worker](https://developers.cloudflare.com/workers/) with a
[D1](https://developers.cloudflare.com/d1/) database. When a player finishes the daily puzzle,
the game sends that day's answers here; the server counts how many players chose each answer,
which the game uses for "% picked", rarity scores and most-common-answer reveals.

It stores no personal data: each browser sends a random id so a game is only counted once.

## API

- `POST /api/result` with `{day, client, sig, cells}` records one finished game.
  `cells` is the nine answers (or `null`), left to right, top to bottom.
- `GET /api/stats?day=YYYY-MM-DD&sig=...` returns `{plays, cells:[{player: count}]}`.

`sig` identifies the exact grid, so if a day's grid ever changes, its counts start fresh.
Answers must be real players from the game data (`src/players.js`), each used once.

## Deploy (Cloudflare dashboard, free plan)

1. **Create the database:** Storage & Databases > D1 > Create database, named `owdoku`.
2. **Create the tables:** open the database's Console tab and run the contents of `schema.sql`.
3. **Set the database ID:** copy the database ID into `database_id` in `wrangler.toml`.
4. **Deploy:** Workers & Pages > Create > Import a repository > this repo, with root directory
   `worker`. Cloudflare deploys again on every push.
5. **Connect the game:** set `API_DEFAULT` in `../index.html` to the Worker's address.

## Free plan limits

About 100,000 requests a day and 100,000 database rows written a day. A finished game writes
up to 10 rows. If a daily limit is reached, the server returns an error until midnight UTC and
the game simply hides pick stats; play is unaffected.

When the player list changes, regenerate `src/players.js` (see `../data-pipeline`).
