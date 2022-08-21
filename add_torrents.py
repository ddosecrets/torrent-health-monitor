#!/usr/bin/env python3
import sys, re, torf
from database import database

# Takes a CSV line, returns (torrent name, magnet, info hash)
def parseLine(line):
	match = re.search(r"([^,]*),(.*)", line)
	name = match.group(1)
	magnet = match.group(2)
	match = re.search(r"urn:btih:([A-Za-z0-9]+)", magnet)
	info_hash = match.group(1)
	return (name,magnet,info_hash)

# Parses CSV file, returns [(torrent name, magnet, info hash), ...]
def parseCSV(filename):
	res = []
	with open(filename, "r") as f:
		lines = f.read().split("\n")[1:-1]
		for line in lines:
			res.append(parseLine(line))
	return res

def addTorrents(torrents):
	with database() as (conn,c):
		for (name,magnet,info_hash) in torrents:
			try:
				m = torf.Magnet.from_string(magnet)
				c.execute("INSERT INTO torrents VALUES(%s,%s,%s) ON CONFLICT DO NOTHING", [name,magnet,info_hash])
				#print("Added %s => %s" % (name,info_hash))
				for tracker in m.tr:
					c.execute("INSERT INTO trackers VALUES(%s,%s) ON CONFLICT DO NOTHING", [info_hash, tracker])
			except torf._errors.URLError as e:
				sys.stderr.write("Invalid magnet link for '%s': '%s' - skipping...\n" % (name,magnet))
				sys.stderr.write(str(e) + "\n")
			except torf._errors.MagnetError as e:
				sys.stderr.write("Invalid magnet link for '%s': '%s' - skipping...\n" % (name,magnet))
				sys.stderr.write(str(e) + "\n")

if __name__ == "__main__":
	if( len(sys.argv) != 2 ):
		sys.stderr.write("USAGE: %s <csvfile>\nWhere csvfile is in the format 'torrent name,magnet link' with a header line\n" % sys.argv[0])
		sys.exit(1)
	csvfile = sys.argv[1]
	res = parseCSV(csvfile)
	addTorrents(res)
