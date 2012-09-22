<html>
	<head>
		<title>Ploddle!</title>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"></script>
		<script src="/static/ploddle.js"></script>
		<link rel="stylesheet" type="text/css" href="/static/ploddle.css">
	</head>
	<body>
		<h1>Ploddle!</h1>
		
		<div id="controls">
			<form id="columns">
			</form>
			<div>
				<a href="#" id="firstpage">&#x21E4;</a>
				<a href="#" id="prevpage">&#x2190;</a>
				<span id="page"></span> /
				<span id="pages"></span>
				<a href="#" id="nextpage">&#x2192;</a>
				<a href="#" id="lastpage">&#x21E5;</a>
			</div>
		</div>

		<form id="filters">
			<input type="hidden" name="page" id="pageinput" value="1">
			<input type="hidden" name="pages" id="pagesinput" value="1">
			<table>
				<thead id="headings">
				</thead>
				<tbody id="messages">
				</tbody>
			</table>
		</form>
	</body>
</html>
