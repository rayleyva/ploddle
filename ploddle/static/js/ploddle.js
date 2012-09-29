


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

		fix_header_widths();
	});
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
	$("#livemode").click(function(e) {
		if(is_live()) {
			start_live();
		}
		else {
			cancel_live();
		}
	});
});
