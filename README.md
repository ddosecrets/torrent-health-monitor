## Torrent Health Monitor

This software suite takes a list of torrents, and for each periodically checks the available peers via torrent trackers and the distributed hash table (DHT). We then create a web interface indicating how many peers we've observed in the last day/week/month, and how many trackers we've been able to contact in the same time frames. This allows us to identify torrents that are unavailable, either because there are no seeds online, or because all trackers for the torrent are offline. If there are no trackers available, users _may_ be able to identify peers via the DHT, but only if their client supports it and is integrated into the swarm already.

### Limitations

We identify the number of peers for each torrent, but not the number of seeds. It isn't possible to determine confidently that a peer is a seed without connecting to every peer directly and asking them what chunks of the torrent they have available, and even then, we can't prove that they're telling the truth without actually _downloading_ all those chunks. Torrent trackers maintain a "seed" count, but this is self-reported by torrent clients, so it's unreliable. Trackers also don't tell us _which_ peers reported themselves as seeds, so we can't aggregate the seed counts across multiple trackers. Therefore, we discard the leecher/seeder distinction and just track unique IP addresses that have indicated interest in a torrent.

We _also_ won't identify peers through [peer exchange](https://en.wikipedia.org/wiki/Peer_exchange), since PEX is only possible when actively connecting to known peers. However, anyone downloading a torrent can only use PEX once they've identified some starting peers through trackers or the DHT, so ignoring PEX is actually appropriate when gauging the availability of a torrent.

### Dependencies

For Ruby:

    gem install bencode base32 pg

For Python:

    pip install psycopg2 mako btdht torf

### Deployment Instructions

To install:

1. First install postgresql, and create a database and sql user for this application. Set the database name, username, and password in `config.json`.

2. Run `./init_db.py` once to initialize all tables and views.

3. Create a long (200+ characters) random string, and set it as `salt` in `config.json`.

4. Add cronjobs to run `scrape_dht.py`, `scrape_torrents.rb`, and `export_html.py` at regular intervals. Hourly should be fine. For example, run `crontab -e` and add the following lines:

```
0  * * * * /path/to/installation/scrape_dht.py
0  * * * * /path/to/installation/scrape_trackers.py
*/10 * * * * /path/to/installation/export_html.py
```

5. Add any torrents you want to monitor, either individually via `./add_torrent.py`, or as a CSV file (with header) of `torrent_name,magnet_link` on each line.

The application will now check the DHT and trackers for each torrent each hour, and every ten minutes will write a new HTML file containing the latest results. Re-exporting the results every 10 minutes means we aren't relying on careful timing to export right after the scraping scripts finish, ensuring the HTML page will list the most recent results, rather than those an hour old.
