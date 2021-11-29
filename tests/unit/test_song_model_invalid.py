import sys
import pytest
from pydantic import ValidationError
sys.path.append('/code/models')
import song_model

SongModel = song_model.SongModel
# from models.song_model import SongModel

"""
	GIVEN a SongModel model
	WHEN a new SongModel is created
	THEN check that the creation shuould fail, because the 
	input is invalid
	"""

def test_song_model_invalid1():
	
	#invalid input, missing "title"
	line = {"artist": "Madonna","difficulty": 100,"level":13,"released": "2015-10-26"}
	with pytest.raises(ValidationError) as exc_info:
		SongModel(**line)
	assert exc_info.value.errors() == [{'loc': ('title',), 'msg': 'field required', 'type': 'value_error.missing'}]

def test_song_model_invalid2():
	
	#invalid input, difficulty should be float
	line = {"artist": "Madonna", "title": "Frozen","difficulty": "hard","level":13,"released": "2015-10-26"}
	with pytest.raises(ValidationError) as exc_info:
		SongModel(**line)
	assert exc_info.value.errors() == [{'loc': ('difficulty',), 'msg': 'value is not a valid float', 'type': 'type_error.float'}]


