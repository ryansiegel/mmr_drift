
from datetime import datetime
import requests
import json
import os

pwd_path = os.path.realpath(__file__).rstrip("curl_leaderboards.py")
stamp = datetime.today().strftime('%Y-%m-%d')
stamp_json = f'{stamp}.json'
latest_json = f'latest.json'
json_file = os.path.join(pwd_path, "json", stamp_json)
latest_file = os.path.join(pwd_path, "json", latest_json)

url = "https://pokemongolive.com/_api/gbl.get_leaderboard"
headers = {
    'authority': 'pokemongolive.com',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://pokemongolive.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://pokemongolive.com/leaderboard/?page=1',
    'accept-language': 'en-US,en;q=0.9',
}

r = requests.post(url, headers=headers)
json_data = json.loads(r.content)

with open(json_file, 'w') as outfile:
    json.dump(json_data, outfile)

with open(latest_file, 'w') as outfile:
    json.dump(json_data, outfile)


