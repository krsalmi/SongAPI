from pymongo import MongoClient
import json
from models.song_model import SongModel
import sys
from models.custom_error import CustomError

# Class that will setup and interact with mongo database
class DataBase():
	def __init__(self):
		#connects to mongo database
		client = MongoClient(host='db',
							port=27017,
							username='root', 
							password='pass',
							authSource="admin")
		self.db = client["song_db"]

	#initialized the database
	def init_db(self):
		db = self.db
		db.songs.drop()
		db.create_collection("songs")
		self.id = 1

	#Interacting with the database often returns
	#a cursor object. This function changes it
	#into a list, which is easier to work with
	def cursor_object_to_list(self, db_cursor):
		list_db = list(db_cursor)
		db_cursor.close()
		return list_db

	#A
	def get_all(self):
		db = self.db
		songs = db.songs.find({},{"_id": False})
		songs = self.cursor_object_to_list(songs)
		return songs

	#B
	def get_level(self, level):
		db = self.db
		try:
			level = int(level)
		except:
			return CustomError(400, "Error, not valid level")
		collected_level = db.songs.find({"level": level},{"_id": False})
		collected_list = self.cursor_object_to_list(collected_level)
		if len(collected_list) == 0:
			return CustomError(404, "No songs match the searched for level")
		return collected_list
	#B
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
	#C
	def search_songs(self, message):
		message = message.lower()
		db = self.db
		out1 = db.songs.find({"artist":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
		out2 = db.songs.find({"title":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
		out_list = list(out1) + list(out2)
		out1.close()
		out2.close()
		return out_list
	#D
	def put_rating(self, song_id, rating):
		db = self.db
		ret = db.songs.update_one(
			{'song_id' : song_id},
			{ '$push': { 'rating': rating}}
		)
		return ret
	#E
	def get_ratings(self, song_id):
		db = self.db
		try:
			song_id = int(song_id)
		except:
			return CustomError(400, "Error, invalid 'song_id'")
		ret = db.songs.find_one({'song_id': song_id}, {'rating':1, '_id': False})
		try:
			rating = ret["rating"]
		except:
			return CustomError(404, "Error, no song with searched for 'song_id' found")
		if not rating:
			return CustomError(404, "Searched for song has no ratings yet")
		return rating

	# Adds data, which is a received as a string 'line' and changed to json, 
	# to database if it passes model checking. song_id is added after check.
	def post(self, line):
		db = self.db
		line = json.loads(line)
		try:
			song = SongModel(**line)
		except:
			return CustomError(400, "Error while model checking! ", sys.exc_info())
		bson_song = song.to_bson()
		bson_song["song_id"] = self.id
		db.songs.insert_one(bson_song)
		self.id += 1


