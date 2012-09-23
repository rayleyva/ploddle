var columns = {
	"host": {
		name: "Host",
		filter: '<select name="host" id="host"></select>',
		init: function() {
			json_to_select("/api/hosts.json", "#host");
			$("#host").change(get_data_event);
		},
		width: "12em",
	},
	"timestamp": {
		name: "Timestamp",
		filter: '<input name="timestamp" id="timestamp" type="date">',
		init: function() {
		},
		render: function(row) {
			return row["timestamp"].substring(0, 16);
		},
		width: "18em",
	},
	"daemon": {
		name: "Daemon",
		filter: '<select name="daemon" id="daemon"></select>',
		init: function() {
			json_to_select("/api/daemons.json", "#daemon");
			$("#daemon").change(get_data_event);
		},
		width: "18em",
	},
	"threadName": {
		name: "Thread",
		filter: '<input name="threadName" id="threadName">',
		init: function() {
			$("#threadName").change(get_data_event);
		},
	},
	"message": {
		name: "Message",
		filter: '<input name="message" id="message">',
		init: function() {
		},
	},
	"source1": {
		name: "Source Function",
		filter: '<input name="module" id="module">',
		init: function() {
		},
		render: function(row) {
			if(row["module"]) {
				return row["module"]+":"+row["funcName"];
			}
			else {
				return "-";
			}
		},
	},
	"source2": {
		name: "Source Code",
		filter: '<input name="module" id="module">',
		init: function() {
		},
		render: function(row) {
			if(row["filename"]) {
				return row["filename"]+":"+row["lineno"];
			}
			else {
				return "-";
			}
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
		titles.append($("<td/>").text(columns[colname].name).css("width", columns[colname].width));
		filters.append($("<td/>").html(columns[colname].filter));
	});

	$("#headings").empty();
	$("#headings").append(titles);
	$("#headings").append(filters);

	$(active_columns).each(function(f, colname) {
		columns[colname].init();
	});

	$(".main").css("top", $("HEADER").height()+1);
	$(".main").css("bottom", $("FOOTER").height()+1);
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

function is_live() {
	return $("#livemode").is(":checked");
}

function render_paginator(p, ps) {
	$("#page").text(p);
	$("#pages").text(ps);
}

function render_row(row) {
	var html_row = $("<tr class='message' />");
	if(row["severity"]) {
		html_row.addClass("severity-"+row["severity"]);
	}
	$(active_columns).each(function(f, colname) {
		var renderer = columns[colname].render ? columns[colname].render : function(row) {return row[colname]};
		html_row.append($("<td/>").text(
			renderer(row)
			//columns[colname].render(row)
		).css("width", columns[colname].width));
	});
    $("#messages").append(html_row);
}

function get_data_event(e) {
	get_data();
}

function get_data(append) {
	if(!append) {
		$("#since").val("");
	}
	$.getJSON(
			"/api/messages.json",
			$("#filters").serialize(),
			function(response)
	{
		render_paginator(response.page, response.pages);
		$("#pageinput").val(response.page);
		$("#pagesinput").val(response.pages);

		if(!append) {
			$("#messages").empty();
		}
    	for (var i = 0; i < response.messages.length; i++) {
			render_row(response.messages[i]);
			if(is_live()) {
				$("#since").val(response.messages[i].timestamp);
			}
    	}
		if(append) {
			$(".main").scrollTop($("#messages").height());
		}
	});
}

function go_to_page(page) {
	if(page >= 1 && page <= parseInt($("#pagesinput").val())) {
		$("#pageinput").val(page);
		get_data();
	}
}
function go_to_relpage(relpage) {
	go_to_page(parseInt($("#pageinput").val()) + relpage);
}

var live_timer = false;
function start_live() {
	$("#pageinput").val(-1);
	get_data();
	live_timer = setInterval(function() {
		get_data(true);
	}, 1000);
	$("#paginator").hide();
}
function cancel_live() {
	if(live_timer) {
		clearInterval(live_timer);
	}
	$("#pageinput").val(1);
	$("#since").val("");
	get_data();
	$("#paginator").show();
}

$(function() {
	render_colsel();
	render_header();
	render_paginator(1, 1);
	get_data();

	$("#firstpage").click(function(e) {
		go_to_page(1);
		return false;
	});
	$("#prevpage").click(function(e) {
		go_to_relpage(-1);
		return false;
	});
	$("#nextpage").click(function(e) {
		go_to_relpage(1);
		return false;
	});
	$("#lastpage").click(function(e) {
		go_to_page(parseInt($("#pagesinput").val()));
		return false;
	});

	$("#livemode").click(function(e) {
		if(is_live()) {
			start_live();
		}
		else {
			cancel_live();
		}
	});
});
