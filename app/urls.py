from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<league_id>', views.league, name='league'),
    path('<league_id>/<home_team_id>/<away_team_id>', views.match, name='match'),
]