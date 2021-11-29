import sys
sys.path.append('/code/')
from application import app
import json

def test_index_page_invalid():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/' page is is posted to (POST)
	THEN check that a '405' status code is returned
	"""
	with app.test_client() as test_client:
		response = test_client.post('/')
		assert response.status_code == 405


def test_get_all_songs_invalid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	and that POST is done incorrectly(per must be a number)
	WHEN the '/get_all_songs' page is posted to (POST)
	THEN check that response is what it should be
	"""
	response = app.test_client().post('/get_all_songs', data={'per':"dog"})
	data = json.loads(response.get_data(as_text=True))
	message = "Error, not a number per which to paginate results"
	assert response.status_code == 400
	assert message in data

def test_get_difficulty_level_invalid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_difficulty_level' page is requested (GET)
	with level parameter (with a level that DOESN'T exist),
	THEN check that response is valid and list of songs fitting 
	searched level are returned
	"""
	response = app.test_client().get('/get_difficulty_level?level=6666')
	data = json.loads(response.get_data(as_text=True))
	message = "No songs match the searched for level"
	assert response.status_code == 404
	assert message in data
	
def test_search_songs_invalid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/search_songs' page is requested (GET)
	with 'message' parameter that is not found
	THEN check that response is valid and list of songs fitting 
	searched message are returned
	"""
	response = app.test_client().get('/search_songs?message=kristiinakatherinesalmi')
	data = json.loads(response.get_data(as_text=True))

	assert response.status_code == 404
	assert "No matches found" in data

def test_add_rating_invalid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/add_song_rating' page receives a
	valid PUT request for a document that doesn't exist
	THEN check that response is valid
	"""
	response = app.test_client().put('/add_song_rating', data={'song_id':30000,'rating':3})
	data = json.loads(response.get_data(as_text=True))
	message = "No such document to update"
	assert response.status_code == 404
	assert message in data

def test_add_rating_invalid_2():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/add_song_rating' page receives a
	invalid PUT request (rating must be between 1 and 5)
	THEN check that response is valid
	"""
	response = app.test_client().put('/add_song_rating', data={'song_id':1,'rating':0})
	data = json.loads(response.get_data(as_text=True))
	message = "Error, raiting must be between 1 and 5 inclusive."
	assert response.status_code == 400
	assert message in data

def test_get_song_rating_invalid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_song_rating' page receives a
	valid GET request with a song_id that DOESN'T exist,
	(and that we have added a rating to in the previous test)
	THEN check that response is valid
	"""
	response = app.test_client().get('/get_song_rating?song_id=33333333333333')
	data = json.loads(response.get_data(as_text=True))
	message = "Error, no song with searched for 'song_id' found"
	assert response.status_code == 404
	assert message in data
