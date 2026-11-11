-- One row per finished daily game (per browser), used to dedupe and to count players per day.
CREATE TABLE IF NOT EXISTS plays (
  day     TEXT NOT NULL,           -- puzzle date, YYYY-MM-DD
  client  TEXT NOT NULL,           -- random id stored in the player's browser; not personal data
  created INTEGER NOT NULL,        -- unix seconds
  PRIMARY KEY (day, client)
);
-- How many players picked each answer in each square.
CREATE TABLE IF NOT EXISTS picks (
  day    TEXT NOT NULL,
  cell   INTEGER NOT NULL,         -- 0..8, left to right, top to bottom
  player TEXT NOT NULL,
  count  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, cell, player)
);
