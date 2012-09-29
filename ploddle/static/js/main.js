var columns = {
	"severity": {
		title: "Sev.",
		filter_html: '<select title="severity" id="severity">'+
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
		title: "Host",
		filter_html: '<select title="host" id="host"></select>',
		init: function() {
			json_to_select("/api/hosts.json", "#host");
		},
	},
	"timestamp": {
		title: "Timestamp",
		filter_html: '<input title="timestamp" id="timestamp" type="date">',
		render: function(row) {
			return row["timestamp"].substring(0, 16);
		},
	},
	"daemon": {
		title: "Daemon",
		filter_html: '<select title="daemon" id="daemon"></select>',
		init: function() {
			json_to_select("/api/daemons.json", "#daemon");
		},
	},
	"threadName": {
		title: "Thread",
		filter_html: '<input title="threadName" id="threadName">',
	},
	"title": {
		title: "Logger Name",
		filter_html: '<input title="name" id="name">',
	},
	"source1": {
		title: "Source Function",
		filter_html: '<input title="module" id="module">',
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
		title: "Source Code",
		filter_html: '<input title="module" id="module">',
		render: function(row) {
			if(row["filetitle"]) {
				return row["filetitle"]+":"+row["lineno"];
			}
			else {
				return "-";
			}
		},
	},
	"message": {
		title: "Message",
		filter_html: '<input title="message" id="message">',
	},
	"debug": {
		title: "Debug Info",
		filter_html: '',
		render: function(row) {
			return JSON.stringify(row);
		},
	},
};



$(function() {
	/* MODELS */
	FilterControlModel = Backbone.Model.extend({
		defaults: {
			name: "filter",
			title: "A Filter",
			enabled: false,
		},

		toggle: function() {
			this.set({enabled: !this.get('enabled')});
		}
	});

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
			console.log("toggle filter: "+self.name);
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
		},
	});

	/* COLLECTIONS */
	FilterControlList = Backbone.Collection.extend({
		model: FilterControlModel
	});

	FilterList = Backbone.Collection.extend({
		model: FilterModel
	});

	RowList = Backbone.Collection.extend({
		model: RowModel
	});

	/* VIEWS */
	FilterControlView = Backbone.View.extend({
		tagName: 'label',
		className: 'filterControl',
		template: _.template($('#filter-control-template').html()),

		events: {
			'click': 'toggle'
		},

		render: function() {
			this.$el.html( this.template( this.model.toJSON() ) );
			return this;
		},

		toggle: function() {
			this.model.toggle();
			this.$el.toggleClass('enabled', this.model.get('enabled'));
		}
	});

	FilterView = Backbone.View.extend({
		tagName: 'td',
		className: 'filter',

		events: {
			'click': 'toggle'
		},

		initialize: function() {
			this.$el.html(this.model.get("title") + "<br>" + this.model.get("filter_html"));
			//this.$el.css('background-image', 'url('+this.model.get('src')+')');
		},

		render: function() {
			return this;
		},

		toggle: function() {
			this.model.toggle();
			this.$el.toggleClass('enabled', this.model.get('enabled'));
		}
	});

	RowView = Backbone.View.extend({
		tagName: 'tr',

		initialize: function() {
			this.model.bind('change', this.render, this);
			this.model.bind('remove', this.remove, this);

			var html = "";
			var self = this;
			$.each(["severity", "timestamp", "message"], function(i, n) {
				html += "<td class='"+n+"'>"+self.model.get(n)+"</td>";
			});
			this.$el.html(html);
			this.$el.addClass('severity-'+this.model.get("severity"));
			this.$el.addClass('message');
		},

		remove: function() {
			this.model.remove();
		}
	});

	PaginatorView = Backbone.View.extend({
		tagName: 'div',
		template: _.template($('#paginator-template').html()),

		events: {
			'click .remove': 'remove'
		},

		render: function() {
			this.$el.html( this.template( this.model.toJSON() ) );
			return this;
		},
	});

	// App view
	var filterControls = new FilterControlList;
	var filters = new FilterList;
	var rows = new RowList;
	var paginator = new PaginatorModel;

	AppView = Backbone.View.extend({
		el: $('#rows'),

		initialize: function() {
			filterControls.on('add', this.addFilterControl, this);
			filters.on('add', this.addFilter, this);
			rows.on('add', this.addRow, this);

			var view = new PaginatorView({model: paginator});
			$('#settings').append( view.render().$el );

			$.each(columns, function(colname, col) {
				filterControls.add({
					name: col.name,
					title: col.title,
				});
			});

			$.each(columns, function(colname, col) {
				filters.add(col);
			});

			$.getJSON(
					"/api/messages.json",
					$("#filters").serialize(),
					function(response)
			{
				//render_paginator(response.page, response.pages);
				for(var i=0; i<response.messages.length; i++) {
					rows.add(response.messages[i]);
				}
			});
		},

		render: function() {

		},

		addFilterControl: function(filterControl) {
			var view = new FilterControlView({model: filterControl});
			$('#controls').append( view.render().$el );
		},

		addFilter: function(filter) {
			var view = new FilterView({model: filter});
			$('#headings').append( view.render().$el );

			$("ARTICLE").css("top", $("HEADER").height()+1);
			$("ARTICLE").css("bottom", $("FOOTER").height()+1);
			$("SECTION.main").css("right", $("SECTION.settings").width()+1);
			$("HEADER").css("padding-right", $("SECTION.settings").width()+1);
		},

		addRow: function(row) {
			var view = new RowView({model: row});
			$('#rows').append( view.render().$el );
		}
	});

	var app = new AppView;
});
