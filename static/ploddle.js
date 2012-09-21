var columns = {
	"severity": {
		name: "Sev.",
		filter: '<select name="severity" id="severity">'+
			'<option value="2">Crit</option>'+
			'<option value="3">Error</option>'+
			'<option value="4">Warn</option>'+
			'<option value="6">Info</option>'+
			'<option value="7" selected>Debug</option>'+
		'</select>',
		init: function() {
			$("#severity").change(get_data);
		},
		render: function(row) {
			return row["severity"];
		},
	},
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
	"source1": {
		name: "Source Function",
		filter: '<input name="module" id="module">',
		init: function() {
		},
		render: function(row) {
			return row["module"]+":"+row["funcName"];
		},
	},
	"source2": {
		name: "Source Code",
		filter: '<input name="module" id="module">',
		init: function() {
		},
		render: function(row) {
			return row["filename"]+":"+row["lineno"];
		},
	},
	"debug": {
		name: "Debug Info",
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
	"message",
	"source2",
];

function json_to_select(url, select) {
	$.getJSON(url, {}, function(data) {
    	$(select).empty();
		$(select).append($('<option value="">All</option>'));
		$(data).each(function(i, val) {
			$(select).append($('<option value="'+val+'">'+val+'</option>'));
    	});
	});
}

function render_header() {
	var titles = $('<tr/>');
	var filters = $("<tr/>");
	$(active_columns).each(function(f, colname) {
		titles.append($("<td/>").text(columns[colname].name));
		filters.append($("<td/>").html(columns[colname].filter));
	});

	$("#headings").empty();
	$("#headings").append(titles);
	$("#headings").append(filters);

	$(active_columns).each(function(f, colname) {
		columns[colname].init();
	});
}

function render_colsel() {
	var list = $("<ul/>");
	$.each(columns, function(colname, colspec) {
		checked = $.inArray(colname, active_columns) >= 0 ? " checked" : "";
		list.append($("<li><label><input type='checkbox' name='"+colname+"' value='"+colname+"'"+checked+"> "+columns[colname].name+"</label>"));
	});
	$("#columns").append(list);

	$("#columns input[type='checkbox']").click(function(e) {
		console.log("Updating columns");
		active_columns = [];
		$("#columns input[type='checkbox']").each(function(i, el) {
			if($(el).is(":checked")) {
				active_columns.push($(el).val());
			}
		});
		render_header();
		get_data();
	});
}

function render_row(row) {
	var html_row = $("<tr/>");
	if(row["severity"]) {
		html_row.addClass("severity-"+row["severity"]);
	}
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
		$("#messages").empty();
    	for (var i = 0; i < response.messages.length; i++) {
			render_row(response.messages[i]);
    	}
	});
}

$(function() {
	render_colsel();
	render_header();
	get_data();
});
