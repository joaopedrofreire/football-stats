from django.shortcuts import render

import http.client
import json

connection = http.client.HTTPConnection('api.football-data.org')
headers = { 'X-Auth-Token': 'f236d854a2394189a0b6adbab1302b70' }
connection.request('GET', '/v2/competitions/2021/matches', None, headers )

response = json.loads(connection.getresponse().read().decode())['matches']

table = response

def index(request):
  context = {'table': table}
    
  return render(request, 'index.html', context)