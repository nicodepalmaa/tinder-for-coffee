from django.urls import path
from . import views

urlpatterns = [
    # Add other URL patterns based on your views
    path('', views.welcome, name='welcome'),
    path('newuser/', views.newuser, name='newuser'),
    path('olduser/', views.olduser, name='oldUser'),
    path('usermenu/', views.usermenu, name='usermenu'),
    path('change-milk-preference/', views.changePreferences, name='changePreferences'),
    #path('recipes/', views.showRecipes, name='recipes'),
    path('recipes/delete/', views.delete_recipe, name='delete_recipe'),
    path('recipes/open/', views.open_recipe, name='open_recipe'),
    path('recipes/search/', views.searchRecipes, name='searchRecipes'),
    path('recipes/search/tinder', views.tinder, name='tinder'),
]
