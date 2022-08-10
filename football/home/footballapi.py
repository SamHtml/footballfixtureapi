from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import re

class scraper:
    def __init__(self,baseurl="https://www.espn.in/football"):
        self.baseurl = baseurl

    # function for scraping data
    def get_fixtures(self,date:str):
        """
        scrape football fixture data from internet 
        parse it append to a dictonary and return it

        date: yyyyddmm [must be this format]
        
        """
        url = f"{self.baseurl}/fixtures/_/date/{date}" 
        # date in format yyyyddmm

        # getting the source of url
        r = requests.get(url)
        # making soup to extract infomation
        soup = BeautifulSoup(r.text, 'html.parser')
        # data will be appended here after extraction
        data={}
        # getting leauge_names on the page
        leauge_names = soup.find_all("h2",attrs={"class":"table-caption"})

        # getting getting other info inside leauge
        for leauge in leauge_names:
            lg_name = leauge.text
            raw_data = leauge.next_sibling.findAll("tr",attrs={"class":["odd","even"]})

            data[lg_name]=[]

            for item in raw_data:
                names = [abbr.get("title") for abbr in item.find_all("abbr")]
                images = []
                # getting the image urls from our system
                for name in names:
                    name = name.replace("/","")
                    name = name.replace("\\","")
                    
                    if os.path.exists(os.path.abspath(f"static/images/logos/{name}.png")):
                        images.append(f"/static/images/logos/{name}.png")
                    else:
                        images.append("/static/images/logos/default.png")
                # getting the game id from span --> a --> href
                gameid = [re.findall(r'\d{4,}',span.find("a",href=True)["href"])[-1] for span in item.find_all("span",attrs={"class":"record"})]
                # getting score from span --> text
                score = [score.text for score in item.find_all("span",attrs={"class":"record"})]
                # getting timings
                timing = [date.get("data-date") for date in item.find_all("td",attrs={"data-behavior":"date_time"})]
                # checking for live
                if timing == []:
                    timing = ["live" for _ in item.find_all("td",attrs={"class":"live"})]
                # checking for TBD
                if timing == []:
                    timing = [time.text for time in item.find_all("a",attrs={"name":"&lpos=null:schedule:time"})]

                # checking for postponed
                if timing == []:
                    timing = [time.text for time in item.find_all("a",attrs={"name":"&lpos=null:schedule:score"}) if time.text == "Postponed"]

                if names == [] and images == [] and timing == []:
                    continue
            
                data[lg_name].append({
                    "teams":names,
                    "logos":images,
                    "timing":timing,
                    "score":score,
                    "gameid":gameid
                    })

        return data

    # for match stats 
    def get_stats(self,matchid):
        # getting url 
        url = f"{self.baseurl}/matchstats?gameId={matchid}"

        # getting the source of url
        r = requests.get(url)
        # making soup to extract infomation
        soup = BeautifulSoup(r.text, 'html.parser')
        # data will be appended here after extraction
        data = {}
        # getting game date
        try:
            game_date_time = soup.find('div',attrs={'class':'game-status'}).find("span",attrs={"data-behavior":"date_time"}).get("data-date")
        except:
            game_date_time =  soup.find('span',attrs={"class":["score", "icon-font-before"],"data-home-away":"home"}).text.strip() +" - "+ soup.find('span',attrs={"class":["score", "icon-font-before"],"data-home-away":"away"}).text.strip()

        home = soup.find("div",attrs={"class":["team away"]}).find("span",attrs={"class":"long-name"}).text
        away = soup.find("div",attrs={"class":["team home"]}).find("span",attrs={"class":"long-name"}).text

        # img urls of teams
        
        # team stats
        home_data = self.get_team_data("teamFormHome",soup)
        away_data = self.get_team_data("teamFormAway",soup)

        data = {
            "datetime" : game_date_time,
            "home_team":home,
            "home_url":self.get_image_url(home),
            "away_team":away,
            "away_url":self.get_image_url(away),
            "home_data":home_data,
            "away_data":away_data
        }
        return data

    def get_image_url(self,name):
        name = name.replace("/","")
        name = name.replace("\\","")
        
        if os.path.exists(os.path.abspath(f"static/images/logos/{name}.png")):
            return f"/static/images/logos/{name}.png"
        else:
            return "/static/images/logos/default.png"
            
    def get_team_data(self,module,soup):
        team_data = [] 
        stats = soup.find("div",attrs={"data-module":module})
        table_data = stats.find("tbody").find_all("tr")
        for tr in table_data:
            try:
                td = tr.find_all("td")
                w_l = td[0].text
                team1 = td[1].find("span",attrs={"class":"long-name"}).text
                team2 = td[5].find("span",attrs={"class":"long-name"}).text
                score = td[3].text
                datetime = td[6].find("span",attrs={"data-behavior":"date_time"}).get("data-date")
                competition = td[7].find("span").text
                team_data.append([w_l,team1,team2,score,datetime,competition])
            except:
                pass

        return team_data
