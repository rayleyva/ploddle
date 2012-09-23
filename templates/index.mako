<html>
	<head>
		<title>Ploddle!</title>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"></script>
		<script src="/static/ploddle.js"></script>
		<link rel="stylesheet" type="text/css" href="/static/ploddle.css">
	</head>
	<body>
		<header>
			<form id="filters">
				<input type="hidden" name="page" id="pageinput" value="1">
				<input type="hidden" id="pagesinput" value="1">
				<input type="hidden" name="since" id="since" value="">
				<table class="messageview" id="headings"></table>
			</form>
		</header>

		<section class="main">
			<table class="messageview" id="messages">
			</table>
		</section>

		<section class="settings">
			<form id="columns">
			</form>
		</section>

		<footer>
			<span id="paginator">
				<a href="#" id="firstpage">&#x21E4;</a>
				<a href="#" id="prevpage">&#x2190;</a>
				<span id="page"></span> /
				<span id="pages"></span>
				<a href="#" id="nextpage">&#x2192;</a>
				<a href="#" id="lastpage">&#x21E5;</a>
			</span>
			&mdash;
			<label><input type="checkbox" id="livemode"> Live Mode</label>
			&mdash;
			<a href="#" id="showsettings">Settings</a>
		</footer>
	</body>
</html>
