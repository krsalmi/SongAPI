from single_song import SingleSong
import sys

raw = {"artist": "kris", "released": "2019-02-02", "difficulty": 5, "level": 7}
raw["song_id"] = 1
raw["rating"] = []

try:
	song = SingleSong(**raw)
except:
	print("Error!", sys.exc_info())
res = song.to_bson()
print(res)

print(song.to_json())