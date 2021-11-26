song_file = "songs.json";

db = db.getSiblingDB("song_db");
// db.animal_tb.drop();


// db.animal_tb.insertMany([
// 	{
// 		"id": 1,
// 		"name": "Lion",
// 		"type": "wild"
// 	},
// 	{
// 		"id": 2,
// 		"name": "Cow",
// 		"type": "domestic"
// 	},
// 	{
// 		"id": 3,
// 		"name": "Tiger",
// 		"type": "wild"
// 	},
// ]);


function read_file_and_populate_db(){

	var file = song_file;

	var reader = new gobal.FileReader();
	reader.onload = function(progressEvent){

		// By lines
		var lines = this.result.split('\n');
		for(var line = 0; line < lines.length; line++){
			line_json = JSON.parse(line)
			db.songs.insertOne(line_json)
		console.log(lines[line]);
		}
	};
	reader.readAsText(file);
};

read_file_and_populate_db();