#!/usr/bin/env python3
from database import database

SCHEMA = """
CREATE TABLE IF NOT EXISTS torrents(
	name TEXT,
	magnet TEXT,
	hash TEXT PRIMARY KEY);

CREATE TABLE IF NOT EXISTS trackers(
	hash TEXT,
	tracker TEXT,
	UNIQUE(hash,tracker));

CREATE TABLE IF NOT EXISTS tracker_availability(
	hash TEXT,
	epoch INT,
	tracker TEXT,
	UNIQUE(hash,epoch,tracker));

CREATE TABLE IF NOT EXISTS peers(
	hash TEXT,
	epoch INT,
	hashed_ip TEXT,
	dht BOOLEAN,
	UNIQUE(hash,epoch,hashed_ip));

CREATE INDEX IF NOT EXISTS time_idx ON peers (hash,epoch);

CREATE OR REPLACE VIEW daily_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 86400
	GROUP BY hash;

CREATE OR REPLACE VIEW weekly_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 604800
	GROUP BY hash;

CREATE OR REPLACE VIEW monthly_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 2592000
	GROUP BY hash;

CREATE OR REPLACE VIEW most_recent_torrent_health (hash,peers)
	AS SELECT hash,peers FROM torrent_health
	INNER JOIN (SELECT hash,MAX(epoch) AS epoch FROM torrent_health GROUP BY hash) AS t1 USING (hash,epoch);

CREATE OR REPLACE VIEW summary (name,magnet,hash,recent,daily,weekly,monthly)
	AS SELECT name,magnet,torrents.hash,r.peers,COALESCE(d.peers,0),COALESCE(w.peers,0),COALESCE(m.peers,0) FROM torrents
	LEFT JOIN most_recent_torrent_health AS r ON torrents.hash=r.hash
	LEFT JOIN daily_peers AS d ON torrents.hash=d.hash
	LEFT JOIN weekly_peers AS w ON torrents.hash=w.hash
	LEFT JOIN monthly_peers AS m ON torrents.hash=m.hash;
"""

if __name__ == "__main__":
	with database() as (conn, c):
		c.execute(SCHEMA)
