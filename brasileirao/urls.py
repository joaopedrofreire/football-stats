from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<league_id>', views.league, name='league'),
]