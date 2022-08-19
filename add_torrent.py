#!/usr/bin/env python3
import sys
from add_torrents import parseLine, addTorrents

# This script adds a single new torrent, from the command-line, without
# needing a CSV file. Convenience script, basically does the same thing
# as add_torrents.py

if __name__ == "__main__":
	if( len(sys.argv) != 3 ):
		sys.stderr.write("USAGE: %s <torrent name> <magnet link>" % sys.argv[0])
		sys.exit(1)
	torrent_name = sys.argv[1]
	magnet = sys.argv[2]
	(name,magnet,info) = parseLine(torrent_name+","+magnet)
	addTorrents([(name,magnet,info)])
