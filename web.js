const express = require('express');
const fs = require('fs');
const port = 8080;
var app = express();
var bodyParser = require('body-parser')
var multer  = require('multer')
var upload = multer({ dest: 'uploads/' })
app.set('trust proxy', 1) // trust first proxy
app.use(express.static('./public'));
const { exec } = require('child_process');

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({extended:true}))

// parse application/json
app.use(bodyParser.json())

app.set("view engine", "ejs");
app.set("views", './views');

app.get("/",function(req,res){
	res.render("index",{});
});
app.post("/gen",upload.single('sample'),function(req,res){
	console.log(req.file);
	console.log(req.body);
	var command = "py -3 script.py "+req.file.path+" "+req.body.bpm+" "+req.body.measures;
	
	exec(command, (err, stdout, stderr) => {
	  if (err) {
		console.error(`exec error: ${err}`);
		return;
	  }
	  res.redirect("/"+stdout.trim());
	});
})
app.listen(port);
