#!/usr/bin/env ruby

=begin
	This is a wrapper for the postgres database, similar to database.py.
	Usage example:

	require_relative "database"

	database() do |conn|
		results = conn.exec("SELECT stuff FROM place").to_a
	end

	As in Python, this wrapper will abstract away connection details and
	automatically close the database connection when the block ends.
=end

require "pg"

def database()
	password = File.read(File.dirname(__FILE__) + "/.postgrespassword").rstrip()
	conn = PG.connect :dbname => "torrent_health", :user => "ddosecrets", :password => password
	yield conn
ensure
	conn.close() if conn
end

# WARNING: does *not* auto-close the connection, use with caution!
def open_database()
	password = File.read(File.dirname(__FILE__) + "/.postgrespassword").rstrip()
	conn = PG.connect :dbname => "torrent_health", :user => "ddosecrets", :password => password
	return conn
end
