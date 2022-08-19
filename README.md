## Torrent Health Monitor

This software suite takes a list of torrents, and for each periodically checks the available peers via torrent trackers and the distributed hash table (DHT). We then create a web interface indicating how many peers we've observed in the last day/week/month, and how many trackers we've been able to contact in the same time frames. This allows us to identify torrents that are unavailable, either because there are no seeds online, or because all trackers for the torrent are offline. If there are no trackers available, users _may_ be able to identify peers via the DHT, but only if their client supports it and is integrated into the swarm already.

### Limitations

We identify the number of peers for each torrent, but not the number of seeds. It isn't possible to determine confidently that a peer is a seed without connecting to every peer directly and asking them what chunks of the torrent they have available, and even then, we can't prove that they're telling the truth without actually _downloading_ all those chunks. Torrent trackers maintain a "seed" count, but this is self-reported by torrent clients, so it's unreliable. Trackers also don't tell us _which_ peers reported themselves as seeds, so we can't aggregate the seed counts across multiple trackers. Therefore, we discard the leecher/seeder distinction and just track unique IP addresses that have indicated interest in a torrent.

We _also_ won't identify peers through [peer exchange](https://en.wikipedia.org/wiki/Peer_exchange), since PEX is only possible when actively connecting to known peers. However, anyone downloading a torrent can only use PEX once they've identified some starting peers through trackers or the DHT, so ignoring PEX is actually appropriate when gauging the availability of a torrent.

### Dependencies

For Ruby:

    gem install bencode base32 pg

For Python:

    pip install psycopg2 mako btdht daemonize

### Deployment Instructions

Pending...
