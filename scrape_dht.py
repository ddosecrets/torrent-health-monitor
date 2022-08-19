#!/usr/bin/env python3
import os, btdht, binascii, hashlib, time, base64
from database import database

"""
	This script is at the heart of our data collection. It's intended to be run
	as a cronjob every five minutes or so. It connects to the DHT, waits a
	minute to find peers, then performs a lookup on each of our torrent hashes
	to determine the number of peers for that torrents. Logs results to our
	database, then exits.
"""

STARTUP_DELAY = 60 # How long to wait for the DHT to peer before querying
INTERVAL_DELAY = 300 # Poll again every 5 minutes
ID = "r9T5uUAuTG00hwKyBkZw"
BIND_PORT = 2987

# Returns a list of torrent hashes to examine
def getTorrentHashes():
	with database() as (conn,c):
		c.execute("SELECT DISTINCT hash FROM torrents")
		return list(map(lambda r: r[0], c.fetchall()))

# Support both hexadecimal and older b32 encoded info hashes
def hashToBinary(info_hash):
	if( len(info_hash) == 40 ):
		return binascii.a2b_hex(info_hash)
	elif( len(info_hash) == 32 ):
		return base64.b32decode(info_hash)
	else:
		raise ValueError("Torrent info hash '%s' is invalid" % info_hash)

# Returns a list of hashed IP addresses peered with a torrent
def getPeers(dht, info_hash, salt):
	peers = dht.get_peers(hashToBinary(info_hash))
	if( peers == None ):
		return set()
	hashed_peers = set()
	for (ip,port) in peers:
		peer = (ip+salt).encode("ascii")
		m = hashlib.sha256(peer).hexdigest()
		hashed_peers.add(m)
	return hashed_peers

def logPeers(torrentPeers):
	epoch = int(time.time())
	with database() as (conn,c):
		for info_hash in torrentPeers.keys():
			num_peers = len(torrentPeers[info_hash])
			for peer in torrentPeers[info_hash]:
				c.execute("INSERT INTO peers VALUES(%s,%s,%s,%s)", [info_hash,epoch,peer,True])

def loadSalt(filename=None):
	if( filename == None ):
		filename = os.path.dirname(os.path.realpath(__file__)) + "/.salt"
	with open(filename, "r") as f:
		return f.read()

def main():
	dht = btdht.DHT(id=ID.encode("ascii"), bind_port=BIND_PORT)
	dht.start()
	salt = loadSalt()
	print("DHT created, waiting to peer...")
	time.sleep(STARTUP_DELAY)
	while( True ):
		hashes = getTorrentHashes()
		torrentPeers = dict()
		for info_hash in hashes:
			torrentPeers[info_hash] = getPeers(dht, info_hash, salt)
			print("Found %3d peers for %s" % (len(torrentPeers[info_hash]), info_hash))
		logPeers(torrentPeers)
		print("Sleeping before next poll")
		time.sleep(INTERVAL_DELAY)

if __name__ == "__main__":
	print("Starting in debug mode, attached to terminal.")
	print("To run in production, run 'start_daemon.py'.")
	main()
