#!/usr/bin/env python3
from daemonize import Daemonize
from scrape_dht import main

"""
	This script is a tiny wrapper to start the same functionality
	as in scrape_dht, but detached from a terminal so
	it can run indefinitely.
"""

PIDFILE = "/tmp/torrent_health.pid"

if __name__ == "__main__":
	print("Starting daemon...")
	daemon = Daemonize(app="torrent_health_daemon", pid=PIDFILE, action=main)
	daemon.start()
	print("Started.")
