var express = require('express');
var fs = require("fs");
var file = "../pinger.db";
var exists = fs.existsSync(file);
var sqlite3 = require("sqlite3").verbose();
var db = new sqlite3.Database(file);
var app = express();
var engines = require('consolidate');
var hogan = require('hogan.js');

app.set('view engine', 'html');
app.set('layout', 'layout');
app.enable('view cache');
app.engine('html', require('hogan-express'));

// String multireplace helper
String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

// HTML string line counter
function count_line_breaks(string_phrase){
	return string_phrase.split("<br>").length;
}

// Transforms target to HTML hightlighted log
String.prototype.highlight = function() {
	var target = this;

	target = target.replaceAll("\n", "<br>").replaceAll("[ ]+", "&nbsp")
								 .replaceAll('INFO', '<span class="label label-success" outline>INFO</span>')
								 .replaceAll('DEBUG', '<span class="label label-primary" outline>DEBUG</span>')
								 .replaceAll('ERROR', '<span class="label label-error" outline>ERROR</span>');
	
	var wrapped = "<table><tr><td class='line-number'><code>";
	var lines = count_line_breaks(target);
	for(i=1; i<lines; i++){
		if(i == lines)
			wrapped += i + "<br>" + (i+1);
		else 
			wrapped += i + "<br>";
	}
	wrapped += "</code></td><td class='content'><code>" + target + "</code></td></tr></table>";

	return wrapped;
};

Array.prototype.parse_hosts = function(){
	return this.forEach( function(element, index) {
	    			element.log = element.log.highlight();
	    			element.hosts = JSON.parse(element.hosts.replaceAll("'", '"'));
	    			element.num_up_hosts = element.hosts.length;
	    			element.num_down_hosts = 0;
	    			if(element.failed_hosts != null){
	    				element.failed_hosts = JSON.parse(element.failed_hosts.replaceAll("'", '"'));
	    				element.date_string = element.date.replaceAll("[ .:-]", "-");
		    			element.hosts.forEach(function(host, hindex){
		    					if(host.url.indexOf("http") == -1)
		    						host.url = "http://" + host.url;
		    					element.failed_hosts.forEach(function(failed, findex){
		    					if(failed.name == host.name){
		    						host.failed = "failed";
		    						element.num_down_hosts += 1;
		    					}
		    				});
		    			});
	    			} else {
	    				element.hosts.forEach(function(host, hindex){
	    						element.date_string = element.date.replaceAll("[ .:-]", "_");
		    					if(host.url.indexOf("http") == -1)
		    						host.url = "http://" + host.url;
		    				});
	    			}
	    			element.num_up_hosts = element.hosts.length - element.num_down_hosts;
	    			if(element.num_down_hosts == 0)
	    				element.num_down_hosts = null;
	    		});
}

app.get('/', function(req, res){
	db.all("SELECT id, date, hosts, failed_hosts, log FROM log", function(err, rows){
	    if(rows == undefined)
	        res.status(404);
	    else {
	    		rows.parse_hosts();
	        res.render('logs', {rows});
	    }
	});
});

// Static route to style
app.get("/kube.min.css", function(req, res){
	var options = {
    root: __dirname + '/views/',
    dotfiles: 'deny',
    headers: {
        'x-timestamp': Date.now(),
        'x-sent': true
    }
  };

	res.sendFile("kube.min.css", options);
});

app.get('/notify', function(req, res){
	db.all("SELECT failed_hosts FROM log", function(err, rows){
	    if(rows == undefined) res.send([]);
	    else res.send(rows[rows.length-1]);
	});
});

//app.post('/ping', function (req, res) {
//  res.send('Not yet implemented');
//});

app.listen(3000);