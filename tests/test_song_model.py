import sys
# sys.path.append('/../models')
sys.path.append('../models')
import song_model

SongModel = song_model.SongModel
# from models.song_model import SongModel

"""
	GIVEN a SongModel model
	WHEN a new SongModel is created
	THEN check that the creation either fails, if input is
		invalid, or that once created, the fields are defined correctly.
		Check also that output to_bson() returns a dict.
	"""

def test_song_model_valid1():
	
	#valid input
	line = {"artist": "The Yousicians","title": "Lycanthropic Metamorphosis","difficulty": 14.6,"level":13,"released": "2016-10-26"}
	song = SongModel(**line)
	bson_output = song.to_bson()
	assert song.artist == "The Yousicians"
	assert song.title == "Lycanthropic Metamorphosis"
	assert song.difficulty == 14.6
	assert song.level == 13
	assert song.released == "2016-10-26"
	assert song.rating == []
	line["rating"] = []
	assert type(bson_output) == dict
	assert bson_output == line

def test_song_model_valid2():
	
	#valid input
	line = {"artist": "Madonna","title": "Frozen","difficulty": 100,"level":13,"released": "2015-10-26"}
	song = SongModel(**line)
	bson_output = song.to_bson()
	assert song.artist == "Madonna"
	assert song.title == "Frozen"
	assert song.difficulty == 100
	assert song.level == 13
	assert song.released == "2015-10-26"
	assert song.rating == []
	line["rating"] = []
	assert type(bson_output) == dict
	assert bson_output == line

def test_song_model_invalid1():
	
	#invalid input, missing "title"
	line = {"artist": "Madonna","difficulty": 100,"level":13,"released": "2015-10-26"}
	song = SongModel(**line)

def test_song_model_invalid2():
	
	#invalid input, difficulty should be float
	line = {"artist": "Madonna", "title": "Frozen","difficulty": "hard","level":13,"released": "2015-10-26"}
	song = SongModel(**line)


