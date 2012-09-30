<html>
	<head>
		<title>Ploddle!</title>
		<link rel="stylesheet/less" href="/static/css/ploddle.less">
		<link rel='icon' type='image/x-icon' href='/static/ploddle.ico'>
		<%
		def var(name):
			return "<%- "+name+" %>"
		def raw(name):
			return "<%= "+name+" %>"
		def code(name):
			return "<% "+name+" %>"
		def checkif():
			return """
			<% if(enabled) { %>
			checked="checked"
			<% } %>
			"""
		%>
	</head>
	<body>
		<header>
			<form id="filters">
				<input type="hidden" name="page" id="pageinput" value="1" />
				<input type="hidden" id="pagesinput" value="1" />
				<input type="hidden" name="since" id="since" value="" />
				<table class="messageview" id="headings"></table>
			</form>
		</header>

		<article>
			<section class="settings">
				<form id="controls"></form>
			</section>

			<section class="main">
				<table class="messageview" id="rows"></table>
			</section>
		</article>

		<footer></footer>

		<div id="js" style="display: none;">
			<script src="/static/js/vendor/jquery-1.8.1.js"></script>
			<script src="/static/js/vendor/underscore.js"></script>
			<script src="/static/js/vendor/backbone.js"></script>
			<script src="/static/js/vendor/less.js"></script>
			<script src="/static/js/main.js"></script>
		</div>

		<script type="text/template" id="paginator-template">
			<div id="paginator">
				<a href="#" class="firstpage">&#x21E4;</a>
				<a href="#" class="prevpage">&#x2190;</a>
				<span id="currentPage">${var("currentPage")|n}</span> /
				<span id="totalPages">${var("totalPages")|n}</span>
				<a href="#" class="nextpage">&#x2192;</a>
				<a href="#" class="lastpage">&#x21E5;</a>
				<br><label><input type="checkbox" class="livemode"> Live Mode</label>
			</div>
		</script>
		<script type="text/template" id="filter-toggle-template">
			<label><input type='checkbox' id='${var("name")|n}' ${checkif()|n}/>${var("title")|n}</label>
		</script>
	</body>
</html>
