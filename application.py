from flask import Flask, request, jsonify
from models.database import DataBase
from models.custom_error import CustomError
import json


PER_PAGE = 10
FILE = "/code/songs.json"

app = Flask(__name__)

@app.before_first_request
def setup_database():
	db = DataBase()
	db.init_db()
	f = open(FILE)
	for line in f:
		ret = db.post(line)
		if type(ret) == CustomError:
			return ret.give_response()
	f.close()
	return jsonify("Database built successfully"),201


@app.route('/', methods=["GET"])
def welcome():
	message = ("Welcome to the song database! The database has been built from 'songs.json', "
	"from the entries that passed the model check. Available routes are: '/get_all_songs', '/get_difficulty_level', "
	"'/search_songs', '/add_song_rating' and '/get_song_rating'.")
	return jsonify(message)


#A
# Displays all songs in the database
@app.route('/get_all_songs', methods=["GET", "POST"])
def get_all_songs():
	db = DataBase()
	if request.method == "GET":
		songs = db.get_all()
		return jsonify(songs)
	else:
		per = request.form.get("per")
		if per != None and per != '0':
			try:
				per = int(per)
			except:
				return CustomError(400, "Error, not a number per which to paginate results").give_response()
			global PER_PAGE
			PER_PAGE = per
			message = "Pagination 'per page' number updated, request pages from '/get_all_songs/<pagenum>'"
			return jsonify(message), 201

@app.route('/get_all_songs/<int:page>', methods=["GET"])
def get_all_songs_paginated(page=None):
	db = DataBase()
	songs = db.get_all()
	if page == None or page < 1:
		return CustomError(400, "Error, not a valid page number").give_response()
	collected = [songs[i:i + PER_PAGE] for i in range(0, len(songs), PER_PAGE)]
	try:
		res = collected[page - 1]
		return jsonify(res)
	except:
		return CustomError(404, "Error, results on that page").give_response()

#B
@app.route('/get_difficulty_level', methods=["GET"])
def get_difficulty_level():
	db = DataBase()
	level = request.args.get('level')
	if level:
		collected_list = db.get_level(level)
		if isinstance(collected_list, CustomError):
			return collected_list.give_response()
		else:
			return jsonify(collected_list)
	else:
		difficulty_ret = db.get_difficulty()
		return jsonify(difficulty_ret)



#C
@app.route('/search_songs', methods=["GET"])
def handle_search():
	message = request.args.get('message')
	if not message:
		return CustomError(400, "Error, 'message' field missing").give_response()
	db = DataBase()
	ret = db.search_songs(message)
	if len(ret) == 0:
		return CustomError(404, "No matches found").give_response()
	return jsonify(ret)


#D
@app.route('/add_song_rating', methods=["PUT"])
def add_rating():
	db = DataBase()
	song_id = request.form.get('song_id')
	rating = request.form.get('rating')
	if not song_id or not rating:
		return CustomError(400, "Error, 'song_id' and 'rating' fields missing").give_response()
	try:
		song_id = int(song_id)
		rating = float(rating)
	except:
		return CustomError(400, "Error, not valid inputs for 'song_id' and 'rating'").give_response()
	if not (1 <= rating <= 5):
			return CustomError(400, "Error, raiting must be between 1 and 5 inclusive.").give_response()
	ret = db.put_rating(song_id, rating)
	if ret.modified_count == 1:
		return jsonify(),204
	else:
		return CustomError(404, "No such document to update").give_response()

#E
@app.route('/get_song_rating', methods=["GET"])
def get_song_rating():
	db = DataBase()
	song_id = request.args.get('song_id')
	if not song_id:
		return CustomError(400, "Error, 'song_id' missing").give_response()
	ratings = db.get_ratings(song_id)
	if isinstance(ratings, CustomError):
		return ratings.give_response()
	ratings.sort()
	ave = sum(ratings) / len(ratings)
	return jsonify({"average": ave, "highest": ratings[-1], "lowest": ratings[0]})


if __name__=='__main__':
	app.run(host="0.0.0.0", port=5000)