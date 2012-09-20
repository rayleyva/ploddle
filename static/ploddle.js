var columns = {
	"host": {
		name: "Host",
		filter: '<select name="host" id="host"></select>',
		init: function() {
			json_to_select("/api/hosts.json", "#host");
			$("#host").change(get_data);
		},
		render: function(row) {
			return row["host"];
		},
	},
	"timestamp": {
		name: "Timestamp",
		filter: '<input name="timestamp" id="timestamp" type="date">',
		init: function() {
		},
		render: function(row) {
			return row["timestamp"];
		},
	},
	"daemon": {
		name: "Daemon",
		filter: '<select name="daemon" id="daemon"></select>',
		init: function() {
			json_to_select("/api/daemons.json", "#daemon");
			$("#daemon").change(get_data);
		},
		render: function(row) {
			return row["daemon"];
		},
	},
	"thread": {
		name: "Thread",
		filter: '<input name="threadName" id="threadName">',
		init: function() {
			$("#threadName").change(get_data);
		},
		render: function(row) {
			return row["threadName"];
		},
	},
	"message": {
		name: "Message",
		filter: '<input name="message" id="message">',
		init: function() {
		},
		render: function(row) {
			return row["message"];
		},
	},
	"source": {
		name: "Source",
		filter: '<input name="module" id="module">',
		init: function() {
		},
		render: function(row) {
			return row["module"]+":"+row["funcName"];
		},
	},
	"all": {
		name: "All",
		filter: '',
		init: function() {
		},
		render: function(row) {
			return JSON.stringify(row);
		},
	},
};

var active_columns = [
	"host",
	"timestamp",
	"daemon",
	"thread",
	"message",
	"source",
	"all",
];

function json_to_select(url, select) {
	$.getJSON(url, {}, function(data) {
    	var options = '';
		options += '<option value="">All</option>';
    	for (var i = 0; i < data.length; i++) {
      		options += '<option value="' + data[i] + '">' + data[i] + '</option>';
    	}
    	$(select).html(options);
	});
}

function render_header() {
	var titles = $('<tr/>');
	var filters = $("<tr/>");
	$(active_columns).each(function(f, colname) {
		titles.append($("<td/>").text(columns[colname].name));
		filters.append($("<td/>").html(columns[colname].filter));
	});
	$("#headings").append(titles);
	$("#headings").append(filters);

	for (var f = 0; f < active_columns.length; f++) {
		columns[active_columns[f]].init();
	}
}

function render_row(row) {
	var html_row = $("<tr/>");
	$(active_columns).each(function(f, colname) {
		html_row.append($("<td/>").text(
			columns[colname].render(row)
		));
	});
    $("#messages").prepend(html_row);
}

function get_data() {
	$.getJSON(
			"/api/messages.json",
			$("#filters").serialize(),
			function(response)
	{
    	for (var i = 0; i < response.messages.length; i++) {
			render_row(response.messages[i]);
    	}
	});
}

$(function() {
	render_header();
	get_data();
});
