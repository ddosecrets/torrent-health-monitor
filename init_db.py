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
CREATE INDEX IF NOT EXISTS time_tracker_idx ON tracker_availability (hash,epoch);

CREATE OR REPLACE VIEW daily_tracker_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 86400
	AND dht=false
	GROUP BY hash;

CREATE OR REPLACE VIEW weekly_tracker_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 604800
	AND dht=false
	GROUP BY hash;

CREATE OR REPLACE VIEW monthly_tracker_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 2592000
	AND dht=false
	GROUP BY hash;

CREATE OR REPLACE VIEW daily_dht_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 86400
	AND dht=true
	GROUP BY hash;

CREATE OR REPLACE VIEW weekly_dht_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 604800
	AND dht=true
	GROUP BY hash;

CREATE OR REPLACE VIEW monthly_dht_peers (hash,peers)
	AS SELECT hash,COUNT(DISTINCT hashed_ip) FROM peers
	WHERE epoch > EXTRACT(epoch FROM now()) - 2592000
	AND dht=true
	GROUP BY hash;

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

CREATE OR REPLACE VIEW daily_trackers (hash,trackers)
	AS SELECT hash,COUNT(DISTINCT tracker) FROM tracker_availability
	WHERE epoch > EXTRACT(epoch FROM now()) - 86400
	GROUP BY hash;

CREATE OR REPLACE VIEW weekly_trackers (hash,trackers)
	AS SELECT hash,COUNT(DISTINCT tracker) FROM tracker_availability
	WHERE epoch > EXTRACT(epoch FROM now()) - 604800
	GROUP BY hash;

CREATE OR REPLACE VIEW monthly_trackers (hash,trackers)
	AS SELECT hash,COUNT(DISTINCT tracker) FROM tracker_availability
	WHERE epoch > EXTRACT(epoch FROM now()) - 2592000
	GROUP BY hash;

CREATE OR REPLACE VIEW summary (name,magnet,hash,daily_trackers,weekly_trackers,monthly_trackers,daily_dht,weekly_dht,monthly_dht,daily_tracker_peers,weekly_tracker_peers,monthly_tracker_peers,daily_peers,weekly_peers,monthly_peers)
	AS SELECT name,magnet,torrents.hash,COALESCE(dt.trackers,0),COALESCE(wt.trackers,0),COALESCE(mt.trackers,0),
		COALESCE(dd.peers,0),COALESCE(wd.peers,0),COALESCE(md.peers,0),
		COALESCE(dtp.peers,0),COALESCE(wtp.peers,0),COALESCE(mtp.peers,0),
		COALESCE(dp.peers,0),COALESCE(wp.peers,0),COALESCE(mp.peers,0)
	FROM torrents
	LEFT JOIN daily_trackers AS dt ON torrents.hash=dt.hash
	LEFT JOIN weekly_trackers AS wt ON torrents.hash=wt.hash
	LEFT JOIN monthly_trackers AS mt ON torrents.hash=mt.hash
	LEFT JOIN daily_dht_peers AS dd ON torrents.hash=dd.hash
	LEFT JOIN weekly_dht_peers AS wd ON torrents.hash=wd.hash
	LEFT JOIN monthly_dht_peers AS md ON torrents.hash=md.hash
	LEFT JOIN daily_tracker_peers AS dtp ON torrents.hash=dtp.hash
	LEFT JOIN weekly_tracker_peers AS wtp ON torrents.hash=wtp.hash
	LEFT JOIN monthly_tracker_peers AS mtp ON torrents.hash=mtp.hash
	LEFT JOIN daily_peers AS dp ON torrents.hash=dp.hash
	LEFT JOIN weekly_peers AS wp ON torrents.hash=wp.hash
	LEFT JOIN monthly_peers AS mp ON torrents.hash=mp.hash;
"""

if __name__ == "__main__":
	with database() as (conn, c):
		c.execute(SCHEMA)
