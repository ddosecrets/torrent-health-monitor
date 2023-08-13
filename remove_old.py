#!/usr/bin/env python3
from database import database
from datetime import datetime

"""
	Prunes database entries over 30 days old, as these records are never
	shown in UI and needlessly log addresses
"""

if __name__ == "__main__":
	one_month = 2592000
	earliest_record = int(datetime.now().strftime("%s")) - one_month
	with database() as (conn,c):
		c.execute("DELETE FROM peers WHERE epoch < %s", [earliest_record])
