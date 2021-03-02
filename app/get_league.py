import http.client
import json

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.offline as opy

from math import *
from statistics import mean
from time import sleep

import dash
import dash_html_components as html
import plotly.graph_objects as go
import plotly.offline as opy
from plotly.subplots import make_subplots

connection = http.client.HTTPConnection('api.football-data.org')

def get_league_data(id):
    while True:
        try:
            # Get league data
            headers = { 'X-Auth-Token': 'f236d854a2394189a0b6adbab1302b70' }
            connection.request('GET', f'/v2/competitions/{id}/teams', None, headers )
            teams = json.loads(connection.getresponse().read().decode())
            # Get league standings
            headers = { 'X-Auth-Token': 'd4f521c3c53643cf8b4d25b82b5307e7' }
            connection.request('GET', f'/v2/competitions/{id}/standings', None, headers )
            table = json.loads(connection.getresponse().read().decode())
            # Get league matches
            headers = { 'X-Auth-Token': '1a5f038db98e4ad0af795efc98ad40fa' }
            connection.request('GET', f'/v2/competitions/{id}/matches', None, headers )
            matches = json.loads(connection.getresponse().read().decode())

            return {'table': table, 'matches': matches, 'teams': teams}
        except:
            sleep(1)

class League(object):
    def __init__(self, id):
        while True:
            try:
                league = get_league_data(id)
                self.infos = league['teams']
                self.teams = league['teams']['teams']
                self.matches = league['matches']['matches']
                self.table = league['table']['standings']
                break
            except:
                sleep(62)
        self.id = id
        self.name = self.infos['competition']['name']
        self.area = self.infos['competition']['area']['name']
        start = self.infos['season']['startDate'][:4]
        end = self.infos['season']['endDate'][:4]
        self.season = start + '-' + end
        self.current_round = self.infos['season']['currentMatchday']

    # def info(time,atributo=None):
    
    def get_table(self,start=1,end=20,columns=None):
        complete = self.table[0]['table']
        table = []
        for team in complete:
            table.append({'position': team['position'],
                        'name': team['team']['name'],
                        'team_id': team['team']['id'],
                        'points': team['points'],
                        'played_games': team['playedGames'],
                        'won': team['won'],
                        'draw': team['draw'],
                        'lost': team['lost'],
                        'goals_for': team['goalsFor'],
                        'goals_against': team['goalsAgainst'],
                        'goal_difference': team['goalDifference'],
                        'percentage': round(100*(team['won']*3+team['draw'])/(team['playedGames']*3),1),
                        'form': team['form']})
        df = pd.DataFrame(table[start-1:end], columns=columns)
        return df

    def best_attack(self):
        table = self.get_table().sort_values(by=["goals_for"], ascending=False).head(n=1).to_dict(orient='records')
        team = Team(self, table[0]['team_id']).infos
        return {'name': team['shortName'], 'goals': table[0]['goals_for'], 'url': team['crestUrl']} 

    def worst_attack(self):
        table = self.get_table().sort_values(by=["goals_for"], ascending=True).head(n=1).to_dict(orient='records')
        team = Team(self, table[0]['team_id']).infos
        return {'name': team['shortName'], 'goals': table[0]['goals_for'], 'url': team['crestUrl']}

    def best_defense(self):
        table = self.get_table().sort_values(by=["goals_against"], ascending=True).head(n=1).to_dict(orient='records')
        team = Team(self, table[0]['team_id']).infos
        return {'name': team['shortName'], 'goals': table[0]['goals_against'], 'url': team['crestUrl']} 

    def worst_defense(self):
        table = self.get_table().sort_values(by=["goals_against"], ascending=False).head(n=1).to_dict(orient='records')
        team = Team(self, table[0]['team_id']).infos
        return {'name': team['shortName'], 'goals': table[0]['goals_against'], 'url': team['crestUrl']}

class Match:
    def __init__(self,league,home_team_id,away_team_id):
        for match in league.matches:
            if match['homeTeam']['id']==int(home_team_id) and match['awayTeam']['id']==int(away_team_id):
                self.infos = match
        self.league = league
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
  
    def get_score(self,team=None):
        if team:
            return self.infos['score']['fullTime'][team]
        return self.infos['score']['fullTime']

    def get_scores(self,length=5):
        if team:
            return self.infos['score']['fullTime'][team]
        return self.infos['score']['fullTime']

    def predict_goals(self, team, size):
        home_team = Team(self.league,self.home_team_id)
        away_team = Team(self.league,self.away_team_id)
        home_attack = home_team.attack('home')
        home_defense = home_team.defense('home')
        away_attack = away_team.attack('away')
        away_defense = away_team.defense('away')
        if team == 'home':
            goals_home_team = []
            for match in self.league.matches:
                score = match['score']['fullTime']['homeTeam']
                if score:
                    goals_home_team.append(int(score))
            predict = home_attack * away_defense * mean(goals_home_team)
            probs = []
            for n in range(0,size):
                probs.append(np.exp(-predict)*np.power(predict, n)/factorial(n))
            return probs
        else:
            goals_away_team = []
            for match in self.league.matches:
                score = match['score']['fullTime']['awayTeam']
                if score:
                    goals_away_team.append(int(score))
            predict = away_attack * home_defense * mean(goals_away_team)
            probs = []
            for n in range(0,size):
                probs.append(np.exp(-predict)*np.power(predict, n)/factorial(n))
            return probs

    def predict_results(self, size=5):
        home_team_goals = self.predict_goals('home',size)
        away_team_goals = self.predict_goals('away',size)
        matrix = []
        for i in home_team_goals:
            line = []
            for j in away_team_goals:
                line.append(round(i*j,4))
            matrix.append(line)
        return matrix

    def top_results(self):
        results = self.predict_results(10)
        results_list = []
        for i in results:
            for j in i:
                results_list.append(j)
        results_list.sort()
        results_list = results_list[::-1]
        top = []
        n = 0
        while n < 5:
            home = 0
            for i in results:
                away = 0
                for j in i:
                    if j == results_list[n]:
                        top.append(([home,away],j*100))
                    away += 1
                home += 1
            n += 1
        return top

    def get_chances(self):
        results = self.predict_results(10)
        home = 0
        away = 0
        i = 0
        for line in results:
            j = 0
            for prob in line:
                if i > j:
                    home += round(100*prob)
                elif j > i:
                    away += round(100*prob)
                j += 1
            i += 1
        return [home,100-home-away,away]

    def get_plot(self, team):
        fig = go.Figure()

        y = np.array(self.predict_goals(team, 6)) * 100
        fig.add_trace(go.Scatter(x=[0,1,2,3,4,5], y=y,
                                 line_shape='spline',
                                 line=dict(width=4, color="black"),
                                 marker=dict(size=10, color="#0F80FF"),
                                 hoverinfo='skip'))
        fig.update_layout(autosize=True,
                          height=120,
                          margin=dict(
                             l=0,
                             r=0,
                             b=0,
                             t=0,
                             pad=4),
                          plot_bgcolor="white",
                          xaxis=dict(fixedrange=True),
                          yaxis=dict(fixedrange=True)
                          )
        plot = opy.plot(fig,
                        auto_open=False,
                        output_type='div',
                        config=dict(
                            displayModeBar=False
                        ))
        return plot

class Team:
    def __init__(self,league,team_id):
        for team in league.teams:
            if team['id']==int(team_id):
                self.infos = team
        self.team_id = int(team_id)
        self.league = league

    def matches(self, local=None):
        matches = self.league.matches
        table = []
        for match in matches:
            if local:
                if match[local]['id']==self.team_id:
                    table.append(match)
            else:
                if match['homeTeam']['id']==self.team_id or match['awayTeam']['id']==self.team_id:
                    table.append(match)
        return table

    def attack(self, local):
        goals = []
        total_goals = []
        if local == 'home':
            for match in self.matches('homeTeam'):
                score = match['score']['fullTime']['homeTeam']
                if score:
                    goals.append(int(score))
            for match in self.league.matches:
                score = match['score']['fullTime']['homeTeam']
                if score:
                    total_goals.append(int(score))
        else:
            for match in self.matches('awayTeam'):
                score = match['score']['fullTime']['awayTeam']
                if score:
                    goals.append(int(score))
            for match in self.league.matches:
                score = match['score']['fullTime']['awayTeam']
                if score:
                    total_goals.append(int(score))
        return mean(goals)/mean(total_goals)

    def defense(self, local):
        goals = []
        total_goals = []
        if local == 'home':
            for match in self.matches('homeTeam'):
                score = match['score']['fullTime']['awayTeam']
                if score:
                    goals.append(int(score))
            for match in self.league.matches:
                score = match['score']['fullTime']['awayTeam']
                if score:
                    total_goals.append(int(score))
        else:
            for match in self.matches('awayTeam'):
                score = match['score']['fullTime']['homeTeam']
                if score:
                    goals.append(int(score))
            for match in self.league.matches:
                score = match['score']['fullTime']['homeTeam']
                if score:
                    total_goals.append(int(score))
        return mean(goals)/mean(total_goals)

    def table(self, league):
        table = league.get_table()
        team_table = table[table['name'] == self.infos['name']]
        return team_table.to_dict(orient='records')[0]

    def get_plot(self, league):
        table = self.table(league)
        data = [int(table['won']),int(table['draw']),int(table['lost'])]
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=['Vitórias','Empates','Derrotas'],
                             values=data, 
                             title=dict(
                                text=str(float(table['percentage']))+'%',
                                font=dict(size=50, color='black')),
                             textinfo="none",
                             hole=.9,
                             marker=dict(colors=['#00B732','#0F80FF','#FC0107']),
                             hoverinfo='value'))

        fig.update_layout(autosize=True,
                          height=300,
                          margin=dict(
                             l=0,
                             r=0,
                             b=0,
                             t=0,
                             pad=4
                          ),
                          legend=dict(
                          orientation="h",
                          xanchor='center',
                          x=0.5,
                          font=dict(size=16)),
                          hoverlabel=dict(bgcolor='white',
                                       font_size=20),)

        plot = opy.plot(fig,
                        auto_open=False,
                        output_type='div',
                        config=dict(
                            displayModeBar=False
                        ))

        return plot

        # def lastest_matches(self, league):
