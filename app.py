from flask import Flask, request, jsonify, redirect, Response
from pymongo import MongoClient
import json

from werkzeug.utils import redirect
from models.validate_schema import cmd
import sys


PER_PAGE = 10

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

def add_to_db(db, line, id):
	line_json = json.loads(line)
	line_json["song_id"] = id
	line_json["rating"] = []
	try:
		db.songs.insert_one(line_json)
	except:
		return jsonify("Error adding to database: ", str(sys.exc_info()))

# @app.route('/', methods=["GET"])
@app.before_first_request
def setup_database():
	db = get_db()
	db.songs.drop()
	db.create_collection("songs")
	db.command(cmd)
	#open file and create json object from each line adding "song_id" and "rating" fields
	i = 1
	f = open("songs.json")
	for line in f:
		add_to_db(db, line, i)
		i += 1
	f.close()
	return jsonify("Database built from 'songs.db'")

@app.route('/', methods=["GET"])
def welcome():
	message = """Welcome to the song database! The database has been built from 'songs.json',
			from the entries that passed the model check. 
			Available routes are: '/get_all_songs', '/get_difficulty_level', '/search_songs', 
			'/add_song_rating' and '/get_song_rating'."""
	return Response(response=json.dumps(message),
		status=200,
		mimetype='application/json')


#A
# Displays all songs in the database
@app.route('/get_all_songs', methods=["GET", "POST"])
def get_all_songs():
	if request.method == "GET":
		db = get_db()
		songs = cursor_object_to_list(db.songs.find({},{"_id": False}))
		return Response(response=json.dumps(songs),
				status=200,
				mimetype='application/json')
	else:
		per = request.args.get('per')
		if per != None and per != '0':
			try:
				per = int(per)
			except:
				return Response(response=json.dumps("Error, not a number per which to paginate results"),
					status=400,
					mimetype='application/json')
			global PER_PAGE
			PER_PAGE = per
			return Response(response=json.dumps("Pagination 'per page' number updated, request pages from '/get_all_songs/<pagenum>'"),
				status=200,
				mimetype='application/json')

@app.route('/get_all_songs/<int:page>', methods=["GET"])
def get_all_songs_paginated(page=None):
	db = get_db()
	songs = cursor_object_to_list(db.songs.find({},{"_id": False}))
	if page == None or page < 1:
		return Response(response=jsonify("Error, not a valid page number"),
			status=400,
			mimetype='application/json')
	page = page - 1
	collected = [songs[i:i + PER_PAGE] for i in range(0, len(songs), PER_PAGE)]
	try:
		res = collected[page]
		return Response(response=jsonify(res),
				status=200,
				mimetype='application/json')
	except:
		return Response(response=jsonify("Error, results on that page"),
			status=400,
			mimetype='application/json')

#B
@app.route('/get_difficulty_level', methods=["GET", "POST"])
def get_difficulty_level():
	db = get_db()
	if request.method == "POST":
		level = request.args.get('level')
		if level:
			level = int(level)
			collected_level = db.songs.find({"level": level},{"_id": False})
			collected_list = cursor_object_to_list(collected_level)
			if len(collected_list) == 0:
				return Response(response=jsonify("No songs matching the searched level"),
				status=200,
				mimetype='application/json')
			return Response(response=jsonify(collected_list),
					status=200,
					mimetype='application/json')
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
		return Response(response=custom_encoder(diff_response),
				status=200,
				mimetype='application/json')



#C
@app.route('/search_songs', methods=["GET"])
def handle_search():
	message = request.args.get('message')
	if not message:
		return Response(response=jsonify("You must search for a song using the parameter 'message'"),
			status=400,
			mimetype='application/json')
	message = message.lower()
	db = get_db()
	out1 = db.songs.find({"artist":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
	out2 = db.songs.find({"title":{ '$regex' : message, '$options' : 'i'}},{'_id': False})
	out_list = list(out1) + list(out2)
	out1.close()
	out2.close()
	if len(out_list) == 0:
		return Response(response=jsonify("No matches found"),
				status=200,
				mimetype='application/json')
	return Response(response=jsonify(out_list),
				status=200,
				mimetype='application/json')


#D
@app.route('/add_song_rating', methods=["PUT"])
def add_rating():
	db = get_db()
	song_id = request.args.get('song_id')
	rating = request.args.get('rating')
	if not (song_id or rating):
		return Response(response=jsonify("Error, you must use parameters 'song_id' and 'rating'."),
			status=400,
			mimetype='application/json')
	else:
		rating = float(rating)
		song_id = int(song_id)
		if not (1 <= rating <= 5):
			return Response(response=jsonify("Error, raiting must be between 1 and 5 inclusive."),
			status=400,
			mimetype='application/json')
		ret = db.songs.update(
			{'song_id' : song_id},
			{ '$push': { 'rating': rating}}
		)
		# even if song w id was not found, update still returns a WriteObject, \
		# in which 'updatedExisting' is False
		return Response(response=jsonify(ret),
				status=200,
				mimetype='application/json')

#E
@app.route('/get_song_rating', methods=["GET"])
def get_song_rating():
	db = get_db()
	song_id = request.args.get('song_id')
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


if __name__=='__main__':
	app.run(host="0.0.0.0", port=5000)