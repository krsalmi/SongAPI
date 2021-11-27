from flask import Flask, jsonify, url_for, redirect, request, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from app import get_db
import json
import sys
from models.single_song import SingleSong


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

	def cursor_object_to_list(db_cursor):
		list_db = list(db_cursor)
		db_cursor.close()
		return list_db

	def get_all(self):
		db = self.db
		songs = self.cursor_object_to_list(db.songs.find({},{"_id": False}))
		return songs

	def get_level(self, level):
		db = self.db
		if not level:
			return jsonify("Error, level missing")
		try:
			level = int(level)
		except:
			return jsonify("Error, not valid level")
		collected_level = db.songs.find({"level": level},{"_id": False})
		collected_list = self.cursor_object_to_list(collected_level)
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
		return diff_response

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
		if not line:
			return ("Error, input missing")
		line["song_id"] = self.id
		try:
			song = SingleSong(**line)
		except:
			print("Error while model checking! ", sys.exc_info())
		db.songs.insert_one(song.to_bson())
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

