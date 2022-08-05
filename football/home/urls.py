from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("api/stat/<slug>",views.stat,name="statapi"),
    path("api/fixture/<slug>",views.fixture,name="fixtureapi"),
    path("",views.home,name="home"),

]
