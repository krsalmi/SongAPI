from flask import Response
import json

# Class to return custom error responses
class CustomError:
	def __init__(self, code, message):
		self.message = message
		self.code = code
	def give_response(self):
		return Response(response=json.dumps(self.message),
					status=self.code,
					mimetype='application/json')

