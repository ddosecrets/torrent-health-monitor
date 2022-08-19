#!/usr/bin/env ruby
require 'thread'
require 'set'
require 'uri'
require 'net/http'
require 'socket'
require 'timeout'
require 'bencode'

InfoHash = "614797344a302a0a909f312df68e918a158ae0ad"
Trackers = ["udp://tracker.coppersurfer.tk:6969", "udp://9.rarbg.to:2920", "udp://tracker.opentrackr.org:1337", "udp://tracker.leechers-paradise.org:6969", "udp://exodus.desync.com:6969"]

#InfoHash = "a5f4435322d88d35e82518e2f1534589f33b2dd6"
#Trackers = File.read("list").split("\n")

#InfoHash = "8cf92b7cd3f022fa5478b84963e89c1dd0af090f"
#Trackers = ["http://tracker.nwps.ws:6969/announce", "http://tracker.winglai.com/announce", "http://fr33dom.h33t.com:3310/announce", "http://exodus.desync.com:6969/announce", "http://torrent.gresille.org/announce", "http://tracker.trackerfix.com/announce", "http://tracker.windsormetalbattery.com/announce", "http://torrent-tracker.ru/announce.php", "http://bigfoot1942.sektori.org:6969/announce", "http://tracker.best-torrents.net:6969/announce", "http://announce.torrentsmd.com:6969/announce", "http://tracker.thepiratebay.org/announce"]
#Trackers = File.read("list2").split("\n")

Buffer_size = 2048
UDP_action_connect = 0
UDP_action_announce = 1
UDP_action_scrape = 2
UDP_listen_port = 1234
UDP_timeout = 5
HTTP_listen_port = 1234
HTTP_timeout = 20 # HTTP is a _lot_ slower than UDP

# HTTP announce protocol is described (kinda) at
# https://www.bittorrent.org/beps/bep_0003.html
# and is amended by a secondary spec at
# https://www.bittorrent.org/beps/bep_0023.html
#
# This looks a lot simpler than the UDP implementation, but only because so
# much heavy lifting is moved to the HTTP layer. In reality this is slow,
# cumbersome, and error-prone, which is why almost all torrents favor the
# four-datagram minimal-parsing UDP tracker protocol that supersedes this one.
def scrapeHTTP(tracker, info_hash)
	peer_id = Random.bytes(20)
	decoded_hash = [info_hash].pack("H*") # Switch from hex string to sha1 bytes
	params = {:info_hash => decoded_hash, :peer_id => peer_id,
		:port => HTTP_listen_port, :uploaded => 0, :downloaded => 0, :left => 0}
	tracker.query = URI.encode_www_form(params)

	begin
		Timeout::timeout(HTTP_timeout) do
			res = Net::HTTP.get_response(tracker)
			if not res.is_a?(Net::HTTPSuccess)
				return nil
			end
			decoded = nil
			# *Some* trackers don't follow the bencode spec correctly when
			# there are zero peers. They *should* return a dictionary with
			# one of:
			#    peersle
			#    peers0:
			#    peersl0:e
			# Which indicate a key of "peers" and a value of empty list 
			# (correct according to spec 3) or empty string (correct in spec 23),
			# or a list containing an empty string (almost right).
			# But *instead* they include only the list terminator and give:
			#    peers0:e
			# Which is just wrong!! And crashes decoders. So we do this little
			# dance, and if decoding fails we strip off the last 'e' and try
			# again, only throwing a *real* exception if we fail to decode twice
			#
			# I don't know whether real torrent clients are this generous,
			# but given how jank the spec is, we'll be a little flexible
			begin
				decoded = BEncode.load(res.body)
			rescue BEncode::DecodeError
				decoded = BEncode.load(res.body[0,res.body.length-1])
			end
			if( decoded.has_key?("failure reason") )
				puts "Error from #{tracker.host}: #{decoded["failure reason"]}"
				return nil
			end

			# On to parsing! Peers can be presented as a list of dictionaries
			# (the original specification 3) or as a compact binary string
			# (amended specification 23), and while there's a flag to politely
			# ask the tracker for one format or another, spec says they can
			# ignore us and give whatever format they prefer. Since we have to
			# support both formats anyway, might as well let the server pick
			# and not bother setting the 'compact' flag.
			puts decoded
			if( decoded["peers"].class == String )
				return decodeCompactPeers(decoded["peers"])
			else
				return decodeDictionaryPeers(decoded["peers"])
			end
		end
	rescue BEncode::DecodeError
		puts "Invalid response from #{tracker.host}"
		return nil
	rescue StandardError
		puts "Invalid response from #{tracker.host}"
		return nil
	rescue Timeout::Error
		puts "Timeout contacting #{tracker.host}"
		return nil
	rescue Errno::ECONNREFUSED
		puts "Connection refused at #{tracker.host}"
		return nil
	rescue Errno::ENETUNREACH
		puts "Unable to reach network of #{tracker.host}"
		return nil
	rescue SocketError
		puts "Could not resolve tracker at #{tracker.host}"
		return nil
	rescue OpenSSL::SSL::SSLError
		# We could blindly trust the cert and connect anyway, but torrent
		# clients probably won't, so for all intents and purposes this tracker
		# is offline
		puts "Invalid TLS certificate at #{tracker.host}"
		return nil
	end
end

# If the tracker gave us an adorable serialized list of dictionaries, then we
# just need to pluck the "ip" field from each, ignoring the "peer id" and
# "port" fields
def decodeDictionaryPeers(peers)
	ips = []
	for peer in peers
		ips.append(peer["ip"])
	end
	return ips
end

# In compact format, the peers are a binary string where each six bytes
# represents a peer. The first four bytes are an IP address, the next two
# are a port number. There are no peer IDs in this scheme.
def decodeCompactPeers(peers)
	ips = []
	if( peers.length % 6 != 0 )
		raise StandardError.new "Peer string is invalid!"
	end
	start = 0
	while( start + 5 < peers.length )
		ip = peers[start,start+4].unpack("l>")[0]
		ip_str = [ip].pack("N").unpack("CCCC").join(".")
		ips.append(ip_str)
		start += 6
	end
	return ips
end

# UDP announce protocol is described (mostly) at
# https://www.bittorrent.org/beps/bep_0015.html
#
# This function performs a four-datagram handshake with a tracker to gather
# peer data on a torrent. It returns nil if we didn't hear back or got a
# malformed datagram from the tracker, or a list of peer IP addresses on success
#
# NOTE: This is IPv4 only. The spec says to only show IPv4 addresses if we send
# a v4 datagram, and v6 addresses if we send a v6, so scraping both requires
# connecting twice and using the same peer_id so the tracker can tell we're the
# same client.
def scrapeUDP(tracker, info_hash)
	protocol_id = 0x41727101980 # Magic constant
	decoded_hash = [info_hash].pack("H*") # Switch from hex string to sha1 bytes
	peer_id = Random.bytes(20)
	transaction_id = Random.bytes(4).unpack("l")[0]
	connection_id = 0
	s = UDPSocket.new

	begin
		Timeout::timeout(UDP_timeout) do
			s.connect(tracker.host, tracker.port)

			# First we need to send a connection request
			connection_request = [protocol_id, UDP_action_connect, transaction_id]
			s.sendmsg connection_request.pack("q>l>l>")

			# If the server likes us, it'll complete the handshake by giving us a
			# new connection id. This little dance prevents UDP address spoofing.
			response = s.recv(Buffer_size)
			(_, response_id, connection_id) = response.unpack("l>l>q>")
			if( response_id != transaction_id )
				puts "Got unexpected response id #{response_id} to our #{transaction_id}"
			end

			# Now we can send our announce request, using the authorized connection_id
			transaction_id = Random.bytes(4).unpack("l")[0]
			announce = [connection_id, UDP_action_announce, transaction_id, decoded_hash,
				peer_id, 0, 0, 0, 0, 0, 0, -1, UDP_listen_port]
			s.sendmsg announce[0,3].pack("q>l>l>") + announce[3] + announce[4] +
				announce[5,announce.length].pack("q>q>q>l>l>l>l>s>")

			# And finally we can read the announce response
			# The first 20 bytes are metadata, the rest are seed information
			announce_response = s.recv(Buffer_size)
			(announce_action, announce_tid, interval, leechers, seeders) = announce_response[0,20].unpack("l>l>l>l>l>")
			printf("Heard back from '#{tracker}'! %d leechers, %d seeders\n", leechers, seeders)
			peers = leechers+seeders

			# The spec is a little... ambiguous here. Some trackers seem to include
			# our own IP address in the list of peers, others do not, but they *do*
			# all include us in the number of leechers. Safest course of action
			# seems to be "only request info on one torrent at a time, and read until
			# there's no more data to be read"
			peer_ips = []
			for i in (0 .. peers-1)
				start = 20 + 6*i
				stop = start+6
				if( announce_response.length < stop )
					puts "Peer data block ends prematurely! Tracker is not following spec!"
					return peer_ips
				end
				(peer_ip,peer_port) = announce_response[start,stop].unpack("l>s>")
				peer_ip_str = [peer_ip].pack("N").unpack("CCCC").join(".")
				peer_ips.append(peer_ip_str)
				#puts "Peer: #{peer_ip_str}"
			end
			return peer_ips
		end
	rescue Timeout::Error
		puts "Timeout connecting to #{tracker}"
		return nil
	rescue SocketError
		puts "Could not resolve tracker at #{tracker.host}"
		return nil
	rescue Errno::ECONNREFUSED
		puts "Could not connect via UDP to #{tracker.host}"
		return nil
	ensure
		s.close
	end
end

# We don't want to include our own IP address as a peer, which means
# we need to *know* our public IP address to filter it out
def getPublicIP()
	url = URI("https://icanhazip.com/")
	res = Net::HTTP.get_response(url)
	if( res.is_a?(Net::HTTPSuccess) )
		return res.body.rstrip
	else
		return nil
	end
end

def scrapeTracker(tracker, info_hash)
	# Magnet links sometimes have the trackers URL encoded
	decoded = URI.decode_www_form(tracker)[0][0]
	uri = URI(decoded)
	if( uri.scheme.start_with?("http") )
		scrapeHTTP(uri, info_hash)
	elsif( uri.scheme == "udp" )
		if( uri.port.nil? )
			raise "Cannot leave port undefined for a UDP tracker '#{tracker}'!"
		end
		scrapeUDP(uri, info_hash)
	else
		raise "Unsupported connection type for tracker #{tracker}"
	end
end

# Multi-thread hitting every tracker, collate results, remove our own IP
# if provided. Returns (number of trackers we reached, {set of peer IP addresses})
def scrapeTrackers(trackers, info_hash, public_ip: nil)
	total_peers = Set.new
	reachable_trackers = 0
	threads = []
	trackers.each { |tracker|
		threads << Thread.new { Thread.current[:peers] = scrapeTracker(tracker, info_hash) }
	}
	threads.each do |t|
		t.join
		unless t[:peers].nil?
			reachable_trackers += 1
			puts "Found peers: #{t[:peers]}"
			total_peers = total_peers.union(t[:peers])
		end
	end
	total_peers.delete?(public_ip)
	#puts "Total peers #{total_peers.size}: #{total_peers}"
	#puts "Total reachable trackers: #{reachable_trackers} / #{trackers.size}"
	return (reachable_trackers, total_peers)
end

if __FILE__ == $0
	public_ip = getPublicIP()
	scrapeTrackers(Trackers, InfoHash, public_ip: public_ip)
end