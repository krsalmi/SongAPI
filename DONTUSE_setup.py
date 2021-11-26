import pymongo
from pymongo import MongoClient
import json
from validate_schema import cmd
from flask import jsonify
import sys

def get_db():
	client = MongoClient(host='db',
							port=27017,
							username='root', 
							password='pass',
							authSource="admin")
	db = client["song_db"]
	print("in get_db")
	return db

def setup_database():
	db = get_db()
	db.songs.drop()
	db.create_collection("songs")
	db.command(cmd)
	#open file and create json object from each line adding "song_id" and "rating" fields
	i = 1
	f = open("songs.json")
	for line in f:
		line_json = json.loads(line)
		line_json["song_id"] = i
		line_json["rating"] = []
		try:
			db.songs.insert_one(line_json)
		except:
			return jsonify("Error adding to database: ", str(sys.exc_info()))
		i += 1
	f.close()
	return jsonify("database built from 'songs.json'")

setup_database()