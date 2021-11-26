from flask import Flask, jsonify, url_for, redirect, request, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from app import get_db
import json
import sys
from models.single_song import SingleSong

app = Flask(__name__)




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
		self.id = 1
	
	def init_db(self, file):
		db = self.db
		db.songs.drop()
		db.create_collection("songs")
		#open file and create json object from each line adding "song_id" and "rating" fields
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
		# if len(collected_list) == 0:
		# 	return Response(response=jsonify("No songs matching the searched level"),
		# 	status=200,
		# 	mimetype='application/json')
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
		try:
			rating = ret["rating"]
		except:
			return jsonify("Error, no song with searched for 'song_id' found")
		else:
			if not rating:
				return jsonify("Searched for song has no ratings yet")
			rating.sort()
			ave = sum(rating) / len(rating)
			return jsonify({"average": ave, "highest": rating[-1], "lowest": rating[0]})

	def post(self, line):
		db = get_db()
		try:
			singleSong = SingleSong(line, self.id)
		except:
			return jsonify("Error while model checking")
		self.id += 1
		db.songs.insert_one(singleSong.make_json)

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



class Index(Resource):
	def get(self):
		return redirect(url_for("students"))


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Student, "/api", endpoint="students")
api.add_resource(Student, "/api/<string:registration>", endpoint="registration")
api.add_resource(Student, "/api/department/<string:department>", endpoint="department")

if __name__ == "__main__":
    app.run(debug=True)