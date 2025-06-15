import os
import requests
import json
import urllib
import asyncio

# Function to get TMDB ID using the TMDB API
def get_tmdb_movie_id(api_key, show_name):
    headers = { 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json;charset=utf-8' }
    url = f'https://api.themoviedb.org/3/search/movie?query={show_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['id']
    return None

# Function to get TMDB ID using the TMDB API
def get_tmdb_tv_id(api_key, show_name):
    show_name = show_name.rsplit(":", 1)[0].strip()
    headers = { 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json;charset=utf-8' }
    url = f'https://api.themoviedb.org/3/search/tv?query={show_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['id']
    return None

def get_or_create_list(access_token, account_id, list_name):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8'
    }

    page = 1
    while True:
        url = f'https://api.themoviedb.org/4/account/{account_id}/lists?page={page}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            lists = data['results']
            for lst in lists:
                if lst['name'].lower() == list_name.lower():
                    return lst['id']
            if page >= data['total_pages']:
                break
            page += 1
        else:
            break

    # Create a new list if not found
    url = 'https://api.themoviedb.org/4/list'
    payload = {
        "name": list_name,
        "description": "",
        "iso_639_1": "en"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return response.json()['id']
    return None

def clear_list(api_key, list_id):
    url = f"https://api.themoviedb.org/4/list/{list_id}/clear"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

def update_list(api_key, media_type, tmdb_ids, list_id):
    url = f'https://api.themoviedb.org/4/list/{list_id}/items'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json;charset=utf-8'
    }
    items = []
    for tmdb_id in tmdb_ids:
        items.append({ 'media_type': media_type, 'media_id': tmdb_id })

    payload = {"items": items}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return True
    else:
        return False

async def process_file(country, media_type):
    print(f"Started processing {media_type} data for {country}")

    if media_type == "tv":
        media_type_title = "TV"
        media_type_tmdb = "tv"
    elif media_type == "films":
        media_type_title = "Films"
        media_type_tmdb = "movie"
    else:
        print(f'Invalid media type: {media_type}')
        return False
    
    list_title = f'Netflix Top 10 {media_type_title} - {country.replace('-', ' ').title()}'
    list_id = get_or_create_list(TMDB_ACCESS_TOKEN, TMDB_ACCOUNT_ID, list_title)

    if not list_id:
        print(f'Failed to get/create list: {list_title}')
        return False

    if not clear_list(TMDB_ACCESS_TOKEN, list_id):
        print(f'Failed to clear list: {list_title}')
        return False

    with open(f'../data/{country}/{media_type}.json', 'r') as file:
        data = json.load(file)

    tmdb_ids = []

    if not data:
        print(f'No data found for {media_type} in {country}')
        return False
    
    for item in data:
        encoded_name = urllib.parse.quote(item['name'])
        if media_type == 'tv':
            tmdb_id = get_tmdb_tv_id(TMDB_API_KEY, encoded_name)
        else:
            tmdb_id = get_tmdb_movie_id(TMDB_API_KEY, encoded_name)

        if tmdb_id:
            tmdb_ids.append(tmdb_id)

    update_list(TMDB_ACCESS_TOKEN, media_type_tmdb, tmdb_ids, list_id)

    print(f'Finished processing {media_type} data for {country} - added {len(tmdb_ids)} {media_type_title}')

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_ACCESS_TOKEN = os.getenv('TMDB_ACCESS_TOKEN')
TMDB_ACCOUNT_ID = os.getenv('TMDB_ACCOUNT_ID')

async def main():
    with open("countries.json") as file:
        countries = json.load(file)

    tasks = []
    for country in countries:
        tasks.append(process_file(country, 'films'))
        tasks.append(process_file(country, 'tv'))

    await asyncio.gather(*tasks)

asyncio.run(main())
