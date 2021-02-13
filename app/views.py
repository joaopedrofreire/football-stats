from django.shortcuts import render
from app.get_league import League, Match, Team

def index(request):
    return render(request, 'index.html', {'title':'Início'})

def league(request,league_id):
    league = League(league_id)
    table = league.get_table().to_dict(orient='records')
    teams = league.teams
    matches = league.matches
    stats = {'best_attack': league.best_attack(),
             'worst_attack': league.worst_attack(),
             'best_defense': league.best_defense(),
             'worst_defense': league.worst_defense()}
    return render(request, 'league.html', {'title': league.area+' '+league.name,
                                           'league': league.infos,
    	                                   'table':table,
    	                                   'teams': teams,
    	                                   'matches': matches,
                                           'stats': stats})

def match(request,league_id,home_team_id,away_team_id):
    league = League(league_id)
    match = Match(league,home_team_id,away_team_id)
    score = match.get_score()
    home_team = Team(league,int(home_team_id))
    away_team = Team(league,int(away_team_id))
    attack = away_team.attack('away')
    top_results = match.top_results()
    chances = match.get_chances()
    results = match.predict_results()
    heatmap = []
    for line in results:
        i=0
        for n in line:
            line[i] = n*100
            i+=1
        heatmap.append(line)
    return render(request, 'match.html', {'title': home_team.infos['shortName']+' x '+away_team.infos['shortName'],
                                          'match': match.infos,
    	                                  'home_team': home_team.infos,
    	                                  'away_team': away_team.infos,
    	                                  'score': score,
    	                                  'attack': attack,
    	                                  'top_results': top_results,
    	                                  'chances': chances,
                                          'heatmap': heatmap
    	                                  })
