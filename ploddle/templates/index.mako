<html>
	<head>
		<title>Ploddle!</title>
        <link rel="stylesheet/less" href="/static/css/ploddle.less">
		<link rel='icon' type='image/x-icon' href='/static/ploddle.ico'>
		<%
		def var(name):
			return "<%= "+name+" %>"
		%>
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

		<article>
			<section class="settings">
				<form id="controls"></form>
			</section>

			<section class="main">
				<table class="messageview" id="rows">
				</table>
			</section>
		</article>

		<footer>
		</footer>

		<div id="js" style="display: none;">
			<script src="/static/js/vendor/jquery-1.8.1.js"></script>
			<script src="/static/js/vendor/underscore.js"></script>
			<script src="/static/js/vendor/backbone.js"></script>
			<script src="/static/js/vendor/less.js"></script>
			<script src="/static/js/main.js"></script>
		</div>

		<script type="text/template" id="paginator-template">
			<div id="paginator">
				<a href="#" id="firstpage">&#x21E4;</a>
				<a href="#" id="prevpage">&#x2190;</a>
				<span id="currentPage">${var("currentPage")|n}</span> /
				<span id="totalPages">${var("totalPages")|n}</span>
				<a href="#" id="nextpage">&#x2192;</a>
				<a href="#" id="lastpage">&#x21E5;</a>
			</div>
			<p><label><input type="checkbox" id="livemode"> Live Mode</label>
		</script>
		<script type="text/template" id="filter-control-template">
			<label><input type='checkbox' id='${var("name")|n}' />${var("title")|n}</label>
		</script>
	</body>
</html>
