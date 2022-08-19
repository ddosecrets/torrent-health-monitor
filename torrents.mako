<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<head>
<title>DDoSecrets Torrent Health Dashboard</title>
<link rel="stylesheet" href="style.css"></link>
</head>
<body>
<h2>DDoSecrets Torrent Health Dashboard</h2>
	<table id="torrents">
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
			<td><a href="https://ddosecrets.com/wiki/${row['name']}">${row["name"]}</a></td>
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
