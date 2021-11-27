from pydantic import BaseModel, Field
import json
from typing import List, Optional, Union

class SingleSong(BaseModel):
	artist: str
	difficulty: float
	level: float
	rating = []
	released: str
	song_id: int
	title: str

	def to_bson(self):
			song = self.dict(by_alias=True, exclude_none=True)
			return song

		
