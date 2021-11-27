from os import error
from flask import jsonify, redirect, Response
from pymongo import MongoClient
import json
from models.single_song import SingleSong
import sys
from models.custom_error import CustomError


class SongModel():
	def __init__(self):
		def get_db():
			client = MongoClient(host='db',
								port=27017,
								username='root', 
								password='pass',
								authSource="admin")
			db = client["song_db"]
			return db
		self.db = get_db()
	
	def init_db(self, file):
		db = self.db
		db.songs.drop()
		db.create_collection("songs")
		self.id = 1
		f = open(file)
		for line in f:
			ret = self.post(line)
			if ret:
				return jsonify("Error building database")
		f.close()
		return jsonify("Database built from 'songs.db'")

	def cursor_object_to_list(self, db_cursor):
		list_db = list(db_cursor)
		db_cursor.close()
		return list_db

	def get_all(self):
		db = self.db
		songs = db.songs.find({},{"_id": False})
		songs = self.cursor_object_to_list(songs)
		return songs

	def get_level(self, level):
		db = self.db
		try:
			level = int(level)
		except:
			return (CustomError("Error, not valid level"))
		collected_level = db.songs.find({"level": level},{"_id": False})
		collected_list = self.cursor_object_to_list(collected_level)
		if len(collected_list) == 0:
			return (CustomError("No songs match the searched for level"))
		return collected_list

	def get_difficulty(self):
		db = self.db
		diff_response = db.songs.aggregate([
		{
			'$group': {
				"_id":None,
				'averageDifficulty': { '$avg': "$difficulty"}
			}
		},
		{
			'$project': {
				'_id': False
				}
			}
		])
		ret = self.cursor_object_to_list(diff_response)
		return ret

	def search_songs(self, message):
		if not message:
			return jsonify("You must search for a song using the parameter 'message'")
		message = message.lower()
		db = self.db
		out1 = db.songs.find({"artist":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
		out2 = db.songs.find({"title":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
		out_list = list(out1) + list(out2)
		out1.close()
		out2.close()
		return out_list

	def get_ratings(self, song_id):
		db = self.db
		if not song_id:
			return jsonify("Error, parameter 'song_id' missing")
		song_id = int(song_id)
		ret = db.songs.find_one({'song_id': song_id}, {'rating':1, '_id': False})
		return ret

		
	def post(self, line):
		db = self.db
		line = json.loads(line)
		try:
			song = SingleSong(**line)
		except:
			return("Error while model checking! ", sys.exc_info())
		bson_song = song.to_bson()
		bson_song["song_id"] = self.id
		db.songs.insert_one(bson_song)
		song = SingleSong(**line, song_id=self.id)
		self.id += 1

	def put_rating(self, song_id, rating):
		db = self.db
		if not (song_id or rating):
			return jsonify("Error, you must use parameters 'song_id' and 'rating'.")
		else:
			rating = float(rating)
			song_id = int(song_id)
			if not (1 <= rating <= 5):
				return jsonify("Error, raiting must be between 1 and 5 inclusive.")
			ret = db.songs.update(
				{'song_id' : song_id},
				{ '$push': { 'rating': rating}}
			)
			# even if song w id was not found, update still returns a WriteObject, \
			# in which 'updatedExisting' is False
			return jsonify(ret)
