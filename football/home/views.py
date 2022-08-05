from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
from .footballapi import scraper

# Create your views here.

# return api view for sixture
@api_view(['GET'])
def fixture(request,slug):
    try:
        if datetime.datetime.strptime(str(slug), '%Y%m%d'):
            data = scraper().get_fixtures(str(slug))
            return Response( data )

    except:
        return Response("an error occured date must be in format yyyymmdd",status=404)

# return api view for stat
@api_view(['GET'])
def stat(request,slug):
    try:
        data = scraper().get_stats(slug)
        return Response( data )

    except:
        return Response("an error occured",status=404)

# return homepage of website
def home(request):
    if request.method == "POST":
        date = request.POST.get("date").replace("-","")
    else:
        date = datetime.date.today().strftime("%Y%m%d")

    return render(request,"index.html",context={"data": scraper().get_fixtures(date), "date":f"{date[6:]} {date[4:6]} {date[:4]}'s"})
