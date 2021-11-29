from pydantic import BaseModel, Field

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

		
