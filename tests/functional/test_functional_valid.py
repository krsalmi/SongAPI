import sys
sys.path.append('/code/')
from application import app
import json

class TestHelper:
	def __init__(self):
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
		self.lines = lines
	def get_lines(self):
		return self.lines

TestHelper.__test__ = False

test_helper = TestHelper()

def test_index_page_valid():
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


def test_get_all_songs_valid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	and songs in songs.json are valid
	WHEN the '/get_all_songs' page is requested (GET)
	THEN check that response is valid and the
	data resembles the lines in input file 'songs.json'
	"""
	lines = test_helper.get_lines()
	response = app.test_client().get('/get_all_songs')
	data = json.loads(response.get_data(as_text=True))
	assert response.status_code == 200
	i = 0
	for item in data:
		if i < len(lines):
			for field in lines[i]:
				assert field in item
		i += 1

def test_get_all_songs_valid_2():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	and that POST is done correctly
	WHEN the '/get_all_songs' page is posted to (POST)
	THEN check that response is valid
	"""
	response = app.test_client().post('/get_all_songs', data=json.dumps({'per':2}), content_type='application/json')
	data = json.loads(response.get_data(as_text=True))
	message = "Pagination 'per page' number updated, request pages from '/get_all_songs/<pagenum>'"
	assert response.status_code == 201
	assert message in data

def test_get_difficulty_level_valid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_difficulty_level' page is requested (GET)
	with no additional parameters,
	THEN check that response is valid and difficulty is returned
	"""
	response = app.test_client().get('/get_difficulty_level')
	data = json.loads(response.get_data(as_text=True))
	lines = test_helper.get_lines()
	ave = sum(line["difficulty"] for line in lines) / len(lines)
	message = "{\"averageDifficulty\": " + str(ave).strip() + "}"
	assert response.status_code == 200
	for item in data:
		assert message == json.dumps(item)

def test_get_difficulty_level_valid_2():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_difficulty_level' page is requested (GET)
	with level parameter (with a level that exists),
	THEN check that response is valid and list of songs fitting 
	searched level are returned
	"""
	response = app.test_client().get('/get_difficulty_level?level=6')
	data = json.loads(response.get_data(as_text=True))
	lines = test_helper.get_lines()
	collected = []
	for line in lines:
		if line["level"] == 6:
			collected.append(line)
	assert response.status_code == 200
	i = 0
	for item in data:
		if i < len(collected):
			for field in collected[i]:
				assert field in item
		i += 1
	
def test_search_songs_valid_1():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/search_songs' page is requested (GET)
	with 'message' parameter
	THEN check that response is valid and list of songs fitting 
	searched message are returned
	"""
	response = app.test_client().get('/search_songs?message=night')
	data = json.loads(response.get_data(as_text=True))
	lines = test_helper.get_lines()
	collected = []
	for line in lines:
		if "night" in line["title"].lower() or "night" in line["artist"].lower():
			collected.append(line)
	assert response.status_code == 200
	i = 0
	for item in data:
		if i < len(collected):
			for field in collected[i]:
				assert field in item
		i += 1
	
def test_add_rating_valid():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/add_song_rating' page receives a
	valid POST request
	THEN check that response is valid
	"""
	response = app.test_client().post('/add_song_rating', 
		data=json.dumps({'song_id':1,'rating':1}), content_type='application/json')
	assert response.status_code == 200

def test_get_song_rating_valid():
	"""
	GIVEN a Flask application is running
	and pytest is run inside the 'flask' container
	WHEN the '/get_song_rating' page receives a
	valid GET request with a song_id that exists,
	(and that we have added a rating to in the previous test)
	THEN check that response is valid
	"""
	response = app.test_client().get('/get_song_rating?song_id=1')
	assert response.status_code == 200
	data = json.loads(response.get_data(as_text=True))
	assert 'lowest' in data
	assert data['lowest'] == 1.0


