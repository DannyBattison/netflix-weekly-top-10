import os
import requests
import json
from bs4 import BeautifulSoup

def extract_json_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        json_data = script_tag.string
        return json.loads(json_data)
    return None

with open("countries.json") as file:
    countries = json.load(file)

for country in countries:
    os.makedirs(f"../data/{country}", exist_ok=True)

    urls = {
        "films": f"https://www.netflix.com/tudum/top10/{country}",
        "tv": f"https://www.netflix.com/tudum/top10/{country}/tv",
    }

    for key, url in urls.items():
        response = requests.get(url)

        if response.status_code == 200:
            json_object = extract_json_from_html(response.text)
            weekly_top_ten = json_object["props"]["pageProps"]["data"]["weeklyTopTen"]

            with open(f"../data/{country}/{key}.json", "w") as file: json.dump(weekly_top_ten, file, indent=4)

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    print(f"Data for {country} has been saved successfully")
