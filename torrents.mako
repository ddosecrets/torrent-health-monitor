<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<head>
<title>DDoSecrets Torrent Health Dashboard</title>
<link rel="stylesheet" href="https://unpkg.com/@sakun/system.css" />
</head>
<body>
	<div class="window" style="width:70rem;margin-left: auto; margin-right: auto;">
		<div class="title-bar"> 
			<button aria-label="Close" class="close"></button>
			<h1 class="title">DDoSecrets Torrent Health Dashboard</h1>
			<button aria-label="Resize" class="resize"></button>
		</div>
		<div class="separator"></div>
		<div class="window-pane" style="height:auto;">
			<p>This dashboard currently tracks ${len(torrents)} torrents. Our most recent peer data is from ${mostrecent}.</p>
			<p>Select a column header to sort by that field. Select the header again to reverse sort order.</p>
			<table id="torrents" style="border-spacing: 10px 0;">
				<thead>
					<th onclick="sortTable(0)">Name</th>
					<th onclick="sortTable(1)">Magnet</th>
					<th onclick="sortTable(2)">Daily Online Trackers</th>
					<th onclick="sortTable(3)">Weekly Online Trackers</th>
					<th onclick="sortTable(4)">Monthly Online Trackers</th>
					<th onclick="sortTable(5)">Daily DHT Peers</th>
					<th onclick="sortTable(6)">Weekly DHT Peers</th>
					<th onclick="sortTable(7)">Monthly DHT Peers</th>
					<th onclick="sortTable(8)">Daily Tracker Peers</th>
					<th onclick="sortTable(9)">Weekly Tracker Peers</th>
					<th onclick="sortTable(10)">Monthly Tracker Peers</th>
					<th onclick="sortTable(11)">Daily Total Peers</th>
					<th onclick="sortTable(12)">Weekly Total Peers</th>
					<th onclick="sortTable(13)">Monthly Total Peers</th>
				</thead>
				<tbody>
				% for row in torrents:
				<tr>
					<td><a href="https://ddosecrets.com/wiki/${row['name']}">${row["shortname"]}</a></td>
					<td><a href="${row['magnet']}">LINK</a></td>
					<td>${row["daily_trackers"]}</td>
					<td>${row["weekly_trackers"]}</td>
					<td>${row["monthly_trackers"]}</td>
					<td>${row["daily_dht"]}</td>
					<td>${row["weekly_dht"]}</td>
					<td>${row["monthly_dht"]}</td>
					<td>${row["daily_tracker_peers"]}</td>
					<td>${row["weekly_tracker_peers"]}</td>
					<td>${row["monthly_tracker_peers"]}</td>
					<td>${row["daily_peers"]}</td>
					<td>${row["weekly_peers"]}</td>
					<td>${row["monthly_peers"]}</td>
				</tr>
				% endfor
				</tbody>
			</table>
		</div>
	</div>
	<script>
const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

// do the work...
document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
  const table = th.closest('table');
  const tbody = table.querySelector('tbody');
  Array.from(tbody.querySelectorAll('tr'))
    .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
    .forEach(tr => tbody.appendChild(tr) );
})));
	</script>
</body>
</html>
