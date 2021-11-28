
import sys
sys.path.append('/code/')
from application import app
import json


def test_index_page_1():
	'''
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/' page is requested (GET)
	THEN check that the response is valid
	'''
	response = app.test_client().get('/')
	message = ("Welcome to the song database! The database has been built from 'songs.json', "
	"from the entries that passed the model check. Available routes are: '/get_all_songs', '/get_difficulty_level', "
	"'/search_songs', '/add_song_rating' and '/get_song_rating'.")
	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 200
	assert message in data

def test_index_page_2():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/' page is is posted to (POST)
	THEN check that a '405' status code is returned
	"""

	# Create a test client using the Flask application configured for testing
	with app.test_client() as test_client:
		response = test_client.post('/')
		assert response.status_code == 405

def test_get_all_songs_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_all_songs' page is requested (GET)
	THEN check that response is valid and the
	data resembles the lines in input file 'songs.json'
	ASSUMING that songs in songs.json are valid
	"""
	file = "/code/songs.json"
	lines = []
	i = 1
	f = open(file)
	for line in f:
		line = json.loads(line)
		line["level"] = float(line["level"])
		line["difficulty"] = float(line["difficulty"])
		line["rating"] = []
		line["song_id"] = i
		lines.append(line)
		i += 1
	f.close()
	response = app.test_client().get('/get_all_songs')
	data = json.loads(response.get_data(as_text=True))
	assert response.status_code == 200
	i = 0
	for item in data:
		if i < len(lines):
			for field in line:
				assert field in item
		i += 1

def test_get_all_songs_2():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_all_songs' page is posted to (POST)
	THEN check that response is valid
	ASSUMING that POST is done correctly
	"""
	response = app.test_client().post('/get_all_songs', data={'per':2})
	data = json.loads(response.get_data(as_text=True))
	message = "Pagination 'per page' number updated, request pages from '/get_all_songs/<pagenum>'"
	assert response.status_code == 201
	assert message in data

def test_add_rating_1():
	response = app.test_client().put('/add_song_rating', data={'song_id':1,'rating':3})
	message = "Pagination 'per page' number updated, request pages from '/get_all_songs/<pagenum>'"
	# data = json.loads(response.get_data(as_text=True))
	assert response.status_code == 204
	assert response.data == 2
	# assert message in data
