from pydantic import BaseModel, Field
# from typing import List, Optional, Union

class SongModel(BaseModel):
	artist: str
	difficulty: float
	level: float
	rating = []
	released: str
	title: str

	def to_bson(self):
			song = self.dict(by_alias=True, exclude_none=True)
			return song

		
