import os
import requests
import json
from bs4 import BeautifulSoup

def extract_titles_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find all <button> elements with no attributes
    return [{"name": btn.text, "rank": idx + 1} for idx, btn in enumerate(soup.find_all('button')) if not btn.attrs]

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
            weekly_top_ten = extract_titles_from_html(response.text)

            with open(f"../data/{country}/{key}.json", "w") as file: json.dump(weekly_top_ten, file, indent=4)

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    print(f"Data for {country} has been saved successfully")
