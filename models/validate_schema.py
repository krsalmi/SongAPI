from collections import OrderedDict


validator = {"$jsonSchema":{
			"bsonType": "object",
			"required": [ "artist", "difficulty", "level", "rating", "released", "song_id", "title"],
			"properties": {
			"artist": {
				"bsonType": [ "string" ],
				"description": "performer of song"
			},
			"difficulty": {
				"bsonType": [ "number" ],
				"description": "difficulty level of song"
			},
			"level": {
				"bsonType": [ "number" ],
				"description": "level of song"
			},
			"rating": {
				"bsonType": [ "array" ],
				"description": "array of given ratings",
				"items": {
					"bsonType": ["int"],
					"minimum": 1,
					"maximum": 5
				},
			},
			"released": {
				"bsonType": [ "string" ],
				"description": "date of release of song"
			},
			"song_id": {
				"bsonType": [ "int" ],
				# "unique": True,
				"minimum": 1,
				"description": "index number of song",
			},
			"title": {
				"bsonType": [ "string" ],
				"description": "title of song"
			}
		}
	}
}
#collMod = Add options to a collection or modify a view definition.
cmd = OrderedDict([('collMod', 'songs'),
		('validator', validator),
		('validationLevel', 'moderate')])