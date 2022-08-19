#!/usr/bin/env python3
from mako.template import Template
from database import database

def loadTemplate():
	with open("torrents.mako", "r") as f:
		return f.read()

FIELDS = ["name","magnet","hash","daily_trackers","weekly_trackers",
	"monthly_trackers","daily_dht","weekly_dht","monthly_dht",
	"daily_tracker_peers","weekly_tracker_peers","monthly_tracker_peers",
	"daily_peers","weekly_peers","monthly_peers"]
FIELDSTRING = ",".join(FIELDS)

def loadSummary():
	rows = []
	with database() as (conn,c):
		#c.execute("""SELECT name,magnet,hash,daily_trackers,weekly_trackers,
			#monthly_trackers,daily_dht,weekly_dht,monthly_dht,
			#daily_tracker_peers,weekly_tracker_peers,monthly_tracker_peers,
			#daily_peers,weekly_peers,monthly_peers FROM summary
			#ORDER BY daily_peers""")
		c.execute("SELECT "+FIELDSTRING+" FROM summary ORDER BY daily_peers")
		res = c.fetchall()
		for r in res:
			row = dict()
			for i,n in enumerate(FIELDS):
				row[n] = r[i]
			rows.append(row)
	return rows

def writeHTML(html):
	with open("index.html", "w") as f:
		f.write(html)

if __name__ == "__main__":
	template = loadTemplate()
	torrents = loadSummary()
	html = Template(template).render(torrents=torrents)
	writeHTML(html)
