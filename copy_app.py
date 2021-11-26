from _typeshed import NoneType
from flask import Flask, request, jsonify
from pymongo import MongoClient
import json
# from setup_db import get_db
import math
import re


'''
List of routes to implement:
- A
  - Returns a list of songs with the data provided by the "songs.json".
  - Add a way to paginate songs.
 
- B
  - Returns the average difficulty for all songs.
  - Takes an optional parameter "level" to filter for only songs from a specific level.
 
- C
  - Returns a list of songs matching the search string.
  - Takes a required parameter "message" containing the user's search string.
  - The search should take into account song's artist and title.
  - The search should be case insensitive.
 
- D
  - Adds a rating for the given song.
  - Takes required parameters "song_id" and "rating"
  - Ratings should be between 1 and 5 inclusive.
 
- E
  - Returns the average, the lowest and the highest rating of the given song id.
  '''

app = Flask(__name__)

def cursor_object_to_list(db_cursor):
	list_db = list(db_cursor)
	db_cursor.close()
	return list_db

def custom_encoder(db_response):
	list_db = cursor_object_to_list(db_response)
	return jsonify(list_db)


def get_db():
	client = MongoClient(host='db',
							port=27017,
							username='root', 
							password='pass',
							authSource="admin")
	db = client["song_db"]
	return db

@app.route('/')
def ping_server():
	return jsonify("Welcome to the song database. To initialize the database, go to /init_db")

#Visit this route to initialize the database (pull it from 'songs.json' file)
@app.route('/init_db')
def setup_database():
	db = get_db()
	db.songs.drop()
	i = 1
	f = open("songs.json")
	for line in f:
		line_json = json.loads(line)
		line_json["song_id"] = i
		line_json["rating"] = []
		db.songs.insert_one(line_json)
		i += 1

	f.close()
	return jsonify("database built from 'songs.json'")





#A
@app.route('/get_all_songs')
@app.route('/get_all_songs/<int:page>',methods=['GET'])
def see_all(page=None):
	db = get_db()
	per_page = 10
	songs = cursor_object_to_list(db.songs.find({},{"_id": False}))
	if page:
		if page < 1:
			return jsonify("Error, not a valid page number")
		page = page - 1
		collected = [songs[i:i + per_page] for i in range(0, len(songs), per_page)]
		print("in pagination, collected: ", collected)
		try:
			res = collected[page]
			return jsonify(res)
		except:
			return jsonify("Error, no results on that page")

	return jsonify(songs)

#B
@app.route('/get_song_difficulty', methods=["GET", "POST"])
def difficulty():
	db = get_db()
	level = request.args.get('level')
	if level:
		level = int(level)
		collected_level = db.songs.find({"difficulty": level},{"_id": False})
		return custom_encoder(collected_level)
	else:
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

		return custom_encoder(diff_response)


#C
@app.route('/search_songs')
def handle_search():
	message = request.args.get('message')
	if not message:
		return("You must search for a song using the parameter 'message'")
	message = message.lower()
	db = get_db()
	out1 = db.songs.find({"artist":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
	out2 = db.songs.find({"title":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
	out_list = list(out1) + list(out2)
	out1.close()
	out2.close()
	return jsonify(out_list)


#D
@app.route('/add_song_rating')
def add_rating():
	db = get_db()
	song_id = request.args.get('song_id')
	rating = request.args.get('rating')
	if not (song_id or rating):
		return jsonify("Error, you must use parameters 'song_id' and 'raiting'.")
	else:
		rating = int(rating)
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

#E
'''
- E
  - Returns the average, the lowest and the highest rating of the given song id.
'''
# @app.route('/get_song_rating')
# def see_rating():
# 	db = get_db()
# 	song_id = request.args.get('song_id')
# 	if not song_id:
# 		return jsonify("Error, parameter 'song_id' missing")
# 	song_id = int(song_id)

# 	ret = db.songs.find_one({'song_id': song_id}, {'rating':1, '_id': False})
# 	if type(ret) != dict:
# 		return jsonify("Error, no song with that searched for 'song_id' found")
# 	else:
# 		rating = ret["rating"].sort()
# 		if not len(rating):
# 			return jsonify("Searched for song has no ratings yet")
# 		ave = sum(rating) / len(rating)
		




# 		return jsonify(rating)



if __name__=='__main__':
	app.run(host="0.0.0.0", port=5000)
