function json_to_select(url, select) {
	$.getJSON(url, {}, function(data) {
    	$(select).empty();
		$(select).append($('<option value="">All</option>'));
		$(data).each(function(i, val) {
			$(select).append($('<option value="'+val+'">'+val+'</option>'));
    	});
	});
}

function fix_header_widths() {
	$("#headings TR:eq(1) TD").each(function(i, el) {
		$(el).width(
			$("#rows TR:eq(1) TD:eq("+i+")").width()
		);
	});
}

var columns = [
	{
		name: "severity",
		title: "Severity",
		filter_html: '<select title="severity" id="severity">'+
			'<option value="2">Crit</option>'+
			'<option value="3">Error</option>'+
			'<option value="4">Warn</option>'+
			'<option value="6">Info</option>'+
			'<option value="7" selected>Debug</option>'+
		'</select>',
		render: function(row) {
			return row.get("severity");
		},
	},
	{
		name: "host",
		title: "Host",
		filter_html: '<select title="host" id="host"></select>',
		init: function() {
			json_to_select("/api/hosts.json", "#host");
		},
		enabled: true,
	},
	{
		name: "timestamp",
		title: "Timestamp",
		filter_html: '<input title="timestamp" id="timestamp" type="date">',
		render: function(row) {
			return row.get("timestamp").substring(0, 16);
		},
		enabled: true,
	},
	{
		name: "daemon",
		title: "Daemon",
		filter_html: '<select title="daemon" id="daemon"></select>',
		init: function() {
			json_to_select("/api/daemons.json", "#daemon");
		},
		enabled: true,
	},
	{
		name: "threadName",
		title: "Thread",
		filter_html: '<input title="threadName" id="threadName">',
	},
	{
		name: "title",
		title: "Logger Name",
		filter_html: '<input title="name" id="name">',
	},
	{
		name: "source1",
		title: "Source Function",
		filter_html: '<input title="module" id="module">',
		render: function(row) {
			if(row.get("module")) {
				return row.get("module")+":"+row.get("funcName");
			}
			else {
				return "-";
			}
		},
	},
	{
		name: "source2",
		title: "Source Code",
		filter_html: '<input title="module" id="module">',
		render: function(row) {
			if(row.get("filetitle")) {
				return row.get("filetitle")+":"+row.get("lineno");
			}
			else {
				return "-";
			}
		},
	},
	{
		name: "message",
		title: "Message",
		filter_html: '<input title="message" id="message">',
		enabled: true,
	},
	{
		name: "debug",
		title: "Debug Info",
		filter_html: '',
		render: function(row) {
			return JSON.stringify(row);
		},
	},
];



$(function() {
	/* MODELS */
	FilterModel = Backbone.Model.extend({
		defaults: {
			name: "filter",
			title: "A Filter",
			filter_html: "<input type='text' name='filter' id='filter'>",
			init: function() {},
			render: function(row) { return row[self.name]; },
			enabled: false,
		},

		initialize: function() {

		},

		toggle: function() {
			this.set({enabled: !this.get('enabled')});
		}
	});

	RowModel = Backbone.Model.extend({
		defaults: {
			severity: 0,
			timestamp: "2000-01-01 00:00:00.000",
			message: "A log message",
		},

		remove: function() {
			this.destroy();
		}
	});

	PaginatorModel = Backbone.Model.extend({
		defaults: {
			currentPage: 1,
			totalPages: 1,
			liveMode: false,
		},
		firstPage: function() {
			if(this.get("currentPage") > 1) {
				this.setCurrentPage(1);
			}
		},
		prevPage: function() {
			if(this.get("currentPage") > 1) {
				this.setCurrentPage(this.get("currentPage") - 1);
			}
		},
		setCurrentPage: function(n) {
			//console.log("Moving to page "+n);
			this.set("currentPage", n);
		},
		setTotalPages: function(n) {
			this.set("totalPages", n);
		},
		nextPage: function() {
			if(this.get("currentPage") < this.get("totalPages")) {
				this.setCurrentPage(this.get("currentPage") + 1);
			}
		},
		lastPage: function() {
			if(this.get("currentPage") < this.get("totalPages")) {
				this.setCurrentPage(this.get("totalPages"));
			}
		},
		toggleLive: function() {
			//console.log("Toggling live mode");
			this.set("liveMode", !this.get("liveMode"));
		},
	});


	/* COLLECTIONS */
	FilterList = Backbone.Collection.extend({
		model: FilterModel
	});

	RowList = Backbone.Collection.extend({
		model: RowModel
	});


	/* VIEWS */
	var filters = new FilterList;
	var rows = new RowList;
	var paginator = new PaginatorModel;

	FilterToggleView = Backbone.View.extend({
		tagName: 'label',
		template: _.template($('#filter-toggle-template').html()),

		events: {
			'click INPUT': 'toggle'
		},

		render: function() {
			this.$el.html( this.template( this.model.toJSON() ) );
			return this;
		},

		toggle: function() {
			this.model.toggle();
			$("TD."+this.model.get("name")).toggle(this.model.get("enabled"));
		}
	});

	FilterControlView = Backbone.View.extend({
		tagName: 'td',
		//className: 'filter',

		events: {
			"filter value changed": "changed",
		},

		initialize: function() {
			this.model.on("change:enabled", this.render, this);
		},

		render: function() {
			if(this.model.get("enabled")) {
				this.$el.html(this.model.get("title") + "<br>" + this.model.get("filter_html"));
				var init = this.model.get("init");
				if(init) init();
			}
			else {
				this.$el.empty();
			}

			$("ARTICLE").css("top", $("HEADER").height()+1);
			$("ARTICLE").css("bottom", $("FOOTER").height()+1);
			$("SECTION.main").css("right", $("SECTION.settings").width()+1);
			$("HEADER").css("padding-right", $("SECTION.settings").width()+1);
			return this;
		},

		changed: function() {
		},
	});

	RowView = Backbone.View.extend({
		tagName: 'tr',

		initialize: function() {
			this.model.bind('remove', this.remove, this);

			this.$el.addClass('severity-'+this.model.get("severity"));
			this.$el.addClass('message');
		},

		render: function() {
			var html = "";
			var self = this;
			_.each(columns, function(el, idx, lst) {
				var data = self.model.get(el.name);
				html += "<td class='"+el.name+"'>"+
					(el.render ?
						el.render(self.model) :
						(data ? data : "-")
					)+
				"</td>";
			});
			this.$el.html(html);
			return this;
		},

		remove: function() {
			this.model.remove();
		}
	});

	PaginatorView = Backbone.View.extend({
		tagName: 'div',
		template: _.template($('#paginator-template').html()),

		events: {
			'click .firstpage': 'firstPage',
			'click .prevpage': 'prevPage',
			'click .nextpage': 'nextPage',
			'click .lastpage': 'lastPage',
			'click .livemode': 'toggleLive',
		},

		initialize: function() {
			this.model.on("change", this.render, this);
		},

		render: function() {
			this.$el.html( this.template( this.model.toJSON() ) );
			return this;
		},

		firstPage: function() {
			this.model.firstPage();
		},
		prevPage: function() {
			this.model.prevPage();
		},
		nextPage: function() {
			this.model.nextPage();
		},
		lastPage: function() {
			this.model.lastPage();
		},
		toggleLive: function() {
			this.model.toggleLive();
		},
	});

	// App view
	AppView = Backbone.View.extend({
		el: $('#rows'),

		initialize: function() {
			filters.on('add', this.addFilter, this);
			filters.on('remove', this.removeFilter, this);
			rows.on('add', this.addRow, this);
			rows.on('remove', this.removeRow, this);

			var view = new PaginatorView({model: paginator});
			$('.settings').prepend( view.render().$el );

			$.each(columns, function(colname, col) {
				filters.add(col);
			});

			$.getJSON(
					"/api/messages.json",
					$("#filters").serialize(),
					function(response)
			{
				paginator.setCurrentPage(response.page);
				paginator.setTotalPages(response.pages);
				for(var i=0; i<response.messages.length; i++) {
					rows.add(response.messages[i]);
				}

				fix_header_widths();
			});
		},

		render: function() {

		},

		addFilter: function(filter) {
			var view = new FilterToggleView({model: filter});
			$('#controls').append( view.render().$el );
			var view = new FilterControlView({model: filter});
			$('#headings').append( view.render().$el );
		},
		removeFilter: function(filter) {
		},

		addRow: function(row) {
			var view = new RowView({model: row});
			$('#rows').append( view.render().$el );
		},
		removeRow: function(row) {
		},
	});

	var app = new AppView;
});
