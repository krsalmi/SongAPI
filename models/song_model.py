from pydantic import BaseModel, Field

# Class that is used for model checking
# to_bson returns a dict of received and
# checked data.
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

		
