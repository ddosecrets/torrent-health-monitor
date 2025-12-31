#!/usr/bin/env python3
from database import database
import time

"""
	This script removes log entries more than 32 days old. We only display
	entries up to a month old in the UI, so these old records will never be
	used and will slowly fill the disk.
"""

if __name__ == "__main__":
	threshold = 2764800 # 32 days in seconds
	earliest_record = int(time.time()) - threshold
	with database() as (conn,c):
		c.execute("DELETE FROM peers WHERE epoch < %s", [earliest_record])
		c.execute("DELETE FROM tracker_availability WHERE epoch < %s", [earliest_record])
