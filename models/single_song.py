from flask import jsonify
import json

class SingleSong:
	def __init__(self, line, id):
		if not line:
			return jsonify("Error, input needed")
		line = json.loads(line)
		self.artist = line["artist"]
		self.difficulty = float(line["difficulty"])
		self.level = float(line["level"])
		self.rating = []
		self.released = line["released"]
		self.song_id = int(id)
		self.title = line["title"]
	
	def make_json(self):
		song_dict = {self.artist, self.difficulty, self.level,
		self.rating, self.released, self.song_id, self.title}
		return jsonify(song_dict)
