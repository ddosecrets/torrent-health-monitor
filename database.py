#!/usr/bin/env python3

'''
	This file provides a wrapper to postgres so we don't have to think about
	the authentication details. Usage example:

	from database import database

	with database() as (conn, cursor):
		cursor.execute("""SELECT * from channels""")
		rows = cursor.fetchall()
'''

import psycopg2, os

DBNAME = "torrent_health"
DBUSER = "ddosecrets"

class database:
	def __enter__(self):
		try:
			password = None
			with open(os.path.dirname(os.path.realpath(__file__)) + "/.postgrespassword", "r") as f:
				password = f.read().rstrip()
			connect_str = "dbname='%s' user='%s' host='localhost' password='%s'" % (DBNAME, DBUSER, password)
			self.conn = psycopg2.connect(connect_str)
			self.cursor = self.conn.cursor()
			return (self.conn, self.cursor)
		except Exception as e:
			print("ERROR could not connect to postgres! " + str(e))
	def __exit__(self, type_, value, traceback):
		self.conn.commit() # Flush changes to postgres if not already done
		self.cursor.close()
		self.conn.close()
		return

# Same as the database wrapper, but WITHOUT automatic cleanup! Use with caution!
# Returns (conn, cursor)
def open_database():
	try:
		password = None
		with open(os.path.dirname(os.path.realpath(__file__)) + "/.postgrespassword", "r") as f:
			password = f.read().rstrip()
		connect_str = "dbname='%s' user='%s' host='localhost' password='%s'" % (DBNAME, DBUSER, password)
		conn = psycopg2.connect(connect_str)
		cursor = conn.cursor()
		return (conn, cursor)
	except Exception as e:
		print("ERROR could not connect to postgres! " + str(e))
