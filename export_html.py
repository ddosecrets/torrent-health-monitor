#!/usr/bin/env python3
import datetime, json, os
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
MAXLENGTH = 30

def shortName(name):
	if( len(name) > MAXLENGTH ):
		return name[0:MAXLENGTH-1] + "…"
	return name

def loadSummary():
	rows = []
	mostrecent = None
	with database() as (conn,c):
		c.execute("SELECT MAX(epoch) FROM peers")
		mostrecent = datetime.datetime.fromtimestamp(c.fetchall()[0][0]).strftime('%c')
		c.execute("SELECT "+FIELDSTRING+" FROM summary ORDER BY daily_peers")
		res = c.fetchall()
		for r in res:
			row = dict()
			for i,n in enumerate(FIELDS):
				row[n] = r[i]
			row["shortname"] = shortName(row["name"])
			rows.append(row)
	return (mostrecent, rows)

def writeHTML(html):
	with open(os.path.dirname(os.path.realpath(__file__)) + "/config.json", "r") as f:
		config = json.loads(f.read())
	with open(config["exportpath"], "w") as f:
		f.write(html)

if __name__ == "__main__":
	template = loadTemplate()
	(mostrecent,torrents) = loadSummary()
	html = Template(template).render(torrents=torrents,mostrecent=mostrecent)
	writeHTML(html)
