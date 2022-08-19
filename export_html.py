#!/usr/bin/env python3
from mako.template import Template
from database import database

def loadTemplate():
	with open("torrents.mako", "r") as f:
		return f.read()

def loadSummary():
	rows = []
	with database() as (conn,c):
		c.execute("SELECT name,magnet,recent,daily,weekly,monthly FROM summary ORDER BY daily")
		res = c.fetchall()
		for (name,magnet,recent,daily,weekly,monthly) in res:
			row = {"name": name, "magnet": magnet, "recent": recent,
				"daily": daily, "weekly": weekly, "monthly": monthly}
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
