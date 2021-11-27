from flask import Flask, request, jsonify, redirect, Response
import json

from models.validate_schema import cmd
import sys

from song_model import SongModel


PER_PAGE = 10

app = Flask(__name__)

@app.before_first_request
def setup_database():
	db = SongModel()
	ret = db.init_db("songs.json")
	if ret:
		return Response(response=json.dumps("Error building database"),
		status=400,
		mimetype='application/json')


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
	db = SongModel()
	if request.method == "GET":
		songs = db.get_all()
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
	db = SongModel()
	songs = db.get_all()
	if page == None or page < 1:
		return Response(response=jsonify("Error, not a valid page number"),
			status=400,
			mimetype='application/json')
	collected = [songs[i:i + PER_PAGE] for i in range(0, len(songs), PER_PAGE)]
	try:
		res = collected[page - 1]
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
	db = SongModel()
	if request.method == "POST":
		level = request.args.get('level')
		collected_list = db.get_level(level)
		if isinstance(collected_list, list):
			if len(collected_list) == 0:
				return Response(response=jsonify("No songs matching the searched level"),
				status=200,
				mimetype='application/json')
			return Response(response=jsonify(collected_list),
					status=200,
					mimetype='application/json')
		else:
			return jsonify("Error, level entered not valid")
	else:
		ret = db.get_difficulty()
		try:
			rating = ret["rating"]
		except:
			return jsonify("Error, no song with searched for 'song_id' found")
		if not rating:
			return jsonify("Searched for song has no ratings yet")
		rating.sort()
		ave = sum(rating) / len(rating)
		return Response(response=jsonify({"average": ave, "highest": rating[-1], "lowest": rating[0]}),
				status=200,
				mimetype='application/json')



#C
@app.route('/search_songs', methods=["GET"])
def handle_search():
	message = request.args.get('message')
	db = SongModel()
	ret = db.search_songs(message)
	if len(ret) == 0:
		return Response(response=jsonify("No matches found"),
				status=200,
				mimetype='application/json')
	return Response(response=jsonify(ret),
				status=200,
				mimetype='application/json')


#D
@app.route('/add_song_rating', methods=["PUT"])
def add_rating():
	db = SongModel()
	song_id = request.args.get('song_id')
	rating = request.args.get('rating')
	ret = db.put_rating(song_id, rating)
		# even if song w id was not found, update still returns a WriteObject, \
		# in which 'updatedExisting' is False
	return Response(response=jsonify(ret),
			status=200,
			mimetype='application/json')

#E
@app.route('/get_song_rating', methods=["GET"])
def get_song_rating():
	db = SongModel()
	song_id = request.args.get('song_id')
	ret = db.get_ratings(song_id)
	return Response(json.dumps(ret),
			status=200,
			mimetype='application/json')

if __name__=='__main__':
	app.run(host="0.0.0.0", port=5000)