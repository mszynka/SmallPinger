var express = require('express');
var fs = require("fs");
var file = "../pinger.db";
var exists = fs.existsSync(file);
var sqlite3 = require("sqlite3").verbose();
var db = new sqlite3.Database(file);
var app = express();

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