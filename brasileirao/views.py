from django.shortcuts import render

import http.client
import json

connection = http.client.HTTPConnection('api.football-data.org')
headers = { 'X-Auth-Token': 'f236d854a2394189a0b6adbab1302b70' }

def get_league_data(id):
    # Get league data
    connection.request('GET', f'/v2/competitions/{id}/teams', None, headers )
    teams = json.loads(connection.getresponse().read().decode())
    # Get league standings
    connection.request('GET', f'/v2/competitions/{id}/standings', None, headers )
    table = json.loads(connection.getresponse().read().decode())['standings']
    # Get league matches
    connection.request('GET', f'/v2/competitions/{id}/matches', None, headers )
    matches = json.loads(connection.getresponse().read().decode())['matches']

    return {'table': table, 'matches': matches, 'teams': teams}

def index(request):
	return render(request, 'index.html')

def league(request,league_id):
    context = get_league_data(league_id)
    area = context['teams']['competition']['area']['name']
    league_name = context['teams']['competition']['name']
    context.update({'title': f'{area} {league_name}'})
    return render(request, 'league.html', context)