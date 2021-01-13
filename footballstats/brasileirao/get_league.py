import http.client
import json

connection = http.client.HTTPConnection('api.football-data.org')
headers = { 'X-Auth-Token': 'f236d854a2394189a0b6adbab1302b70' }
connection.request('GET', '/v2/competitions/', None, headers )

leagues = json.loads(connection.getresponse().read().decode())['competitions']

class League:
	def __init__(self, name):
	    self.name = name

	def __repr__(self):
		competition = 
		return ''



		         # positions=True,
		         # names=True,
		         # points=True,
		         # games=True,
		         # won=True,
		         # draw=True,
		         # lost=True,
		         # goals_for=False,
		         # goals_against=False,
		         # goals_difference=False,
		         # form=False