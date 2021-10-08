import requests
from bs4 import BeautifulSoup


def get_fixtures(date:str):
    """
    scrape football fixture data from internet 
    parse it append to a dictonary and return it

    date: yyyyddmm [must be this format]
    
    """
    url = f"https://www.espn.in/football/fixtures/_/date/{date}"
    # date in format yyyyddmm

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')

    data={}

    leauge_names = soup.find_all("h2",attrs={"class":"table-caption"})

    for leauge in leauge_names:
        lg_name = leauge.text
        raw_data = leauge.next_sibling.findAll("tr",attrs={"class":["odd","even"]})

        data[lg_name]=[]

        for item in raw_data:
            names = [abbr.get("title") for abbr in item.find_all("abbr")]
            images = [img.get("src") for img in item.find_all("img")]
            timing = [date.get("data-date") for date in item.find_all("td",attrs={"data-behavior":"date_time"})]
            if timing == []:
                timing = ["live" for _ in item.find_all("td",attrs={"class":"live"})]
            
            if names == [] and images == [] and timing == []:
                continue

            data[lg_name].append((names,images,timing))

    return data


