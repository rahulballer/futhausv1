import requests
import pandas as pd
import re
from dotenv import load_dotenv
import os
from uuid import uuid4


# Load the .env file
load_dotenv('/Users/rahulrangarajan/FootyBreak/futhaus/y/.env')

# Access environment variables
HASURA_GRAPHQL_ENDPOINT = os.getenv('VITE_HASURA_GRAPHQL_ENDPOINT')
HASURA_ADMIN_SECRET = os.getenv('VITE_HASURA_ADMIN_SECRET')

# Now you can use these variables in your headers for Hasura requests
hasura_headers = {
    'Content-Type': 'application/json',
    'x-hasura-admin-secret': HASURA_ADMIN_SECRET
}

# The GraphQL mutation template for inserting data
mutation = """
mutation insertData($objects: [sofascore_insert_input!]!) {
  insert_sofascore(objects: $objects) {
    returning {
      id
      club
      club_url
      club_avatar
      league
      league_url
      league_avatar
      person
      person_url
      person_avatar
      person_id
      person_country
      role
    }
  }
}
"""

# Function to insert data into Hasura
def insert_data_to_hasura(dataframe):
    # Convert your DataFrame to a list of dictionaries
    data_to_insert = dataframe.to_dict(orient='records')
    
    # Make the request to Hasura
    response = requests.post(
        HASURA_GRAPHQL_ENDPOINT, 
        json={'query': mutation, 'variables': {'objects': data_to_insert}},
        headers=hasura_headers
    )
    
    # Check for errors
    if response.status_code == 200:
        print("Data inserted successfully!")
        response_data = response.json()
        print("Response from Hasura:", response_data)
        
        # Check if any data is returned in the 'returning' field
        if not response_data.get('data', {}).get('insert_sofascore', {}).get('returning'):
            print("No data returned. Possible insertion error.")
    else:
        print(f"Failed to insert data: {response.text}")


# Function to fetch and parse JSON data
def fetch_json(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()

# Provided headers
headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"9857b2af5d"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'If-Modified-Since': 'Thu, 01 Jan 2023 00:00:00 GMT'
}

# League URLs with their corresponding season IDs
leagues = {
    'https://www.sofascore.com/tournament/football/germany/bundesliga/35': '52608', #bundesliga
    'https://www.sofascore.com/tournament/football/spain/laliga/8': '52376', #laliga
    'https://www.sofascore.com/tournament/football/england/premier-league/17': '52186', #premier league
    'https://www.sofascore.com/tournament/football/france/ligue-1/34': '52571', #ligue 1
    'https://www.sofascore.com/tournament/football/italy/serie-a/23': '52760', #serie a
    'https://www.sofascore.com/tournament/football/netherlands/eredivisie/37': '52554', #eredivisie
    'https://www.sofascore.com/tournament/football/brazil/brasileirao-serie-a/325': '48982', #brasileirao
    'https://www.sofascore.com/tournament/football/usa/mls/242': '57317', #mls
    'https://www.sofascore.com/tournament/football/turkey/trendyol-super-lig/52': '53190', #super lig turkey
    'https://www.sofascore.com/tournament/football/portugal/liga-portugal/238': '52769', #liga portugal
    'https://www.sofascore.com/tournament/football/scotland/premiership/36': '52588', #scottish premiership
    'https://www.sofascore.com/tournament/football/saudi-arabia/saudi-pro-league/955': '53241', #saudi pro league
    'https://www.sofascore.com/tournament/football/austria/bundesliga/45': '52524', #austria bundesliga
    'https://www.sofascore.com/tournament/football/germany/2-bundesliga/44': '52607', #2. bundesliga
    'https://www.sofascore.com/tournament/football/england/championship/18': '52367', #championship
    'https://www.sofascore.com/tournament/football/spain/laliga-2/54': '52563', #la liga 2
    'https://www.sofascore.com/tournament/football/italy/serie-b/53': '52947', #serie b
    'https://www.sofascore.com/tournament/football/france/ligue-2/182': '52572', #ligue 2

    
}

# Base API URL
base_api_url = 'https://api.sofascore.com/api/v1/'

# Initialize DataFrame
df = pd.DataFrame(columns=['id','league', 'league_url', 'league_avatar', 'club', 'club_url', 'club_avatar', 'person', 'person_url', 'person_avatar', 'person_country', 'role', 'person_id'])

# Process each league
for league_url, season_id in leagues.items():
    league_id = re.search(r'/(\d+)$', league_url).group(1)
    league_avatar_url = f'{base_api_url}unique-tournament/{league_id}/image/dark'
    standings_url = f'{base_api_url}unique-tournament/{league_id}/season/{season_id}/standings/total'

    standings_data = fetch_json(standings_url, headers)
    if not standings_data or 'standings' not in standings_data:
        continue

    league_name = standings_data['standings'][0]['tournament']['name']

    for team_data in standings_data['standings'][0]['rows']:
        team = team_data['team']
        club_avatar_url = f'{base_api_url}team/{team["id"]}/image'
        club_url = f'https://www.sofascore.com/team/football/{team["slug"]}/{team["id"]}'

        team_details_url = f'{base_api_url}team/{team["id"]}'
        team_details = fetch_json(team_details_url, headers)
        manager = team_details['team'].get('manager', {})

        # Generate a unique ID for each row using uuid4
        unique_id = str(uuid4())

        if manager:
            manager_avatar_url = f'{base_api_url}manager/{manager.get("id", "")}/image'
            manager_id = manager['id']
            manager_url = f'https://www.sofascore.com/manager/{manager.get("slug", "")}/{manager.get("id", "")}'
            manager_country = manager.get('country', {}).get('name', '')
            df = df._append({'league': league_name, 'league_url': league_url, 'league_avatar': league_avatar_url,
                            'club': team['name'], 'club_url': club_url, 'club_avatar': club_avatar_url, 
                            'person': manager.get('name', ''), 'person_url': manager_url, 
                            'person_avatar': manager_avatar_url, 'person_country': manager_country, 'person_id' : manager_id, 'id': unique_id,
                            'role': 'Manager'}, ignore_index=True)

        players_url = f'{base_api_url}team/{team["id"]}/players'
        players_data = fetch_json(players_url, headers)

        if not players_data:
            continue

        player_names = set()

        for player_info in players_data['players']:
            player = player_info['player']
            player_name = player['name']

            if player_name in player_names:
                continue

            player_names.add(player_name)
            player_id = player['id']
            player_avatar_url = f'{base_api_url}player/{player_id}/image'
            player_url = f'https://www.sofascore.com/player/{player["slug"]}/{player_id}'
            player_country = player.get('country', {}).get('name', '')
            # Generate a unique ID for each row using uuid4
            unique_id = str(uuid4())
            df = df._append({'league': league_name, 'league_url': league_url, 'league_avatar': league_avatar_url,
                            'club': team['name'], 'club_url': club_url, 'club_avatar': club_avatar_url, 
                            'person': player_name, 'person_url': player_url, 
                            'person_avatar': player_avatar_url, 'person_country': player_country, 'person_id': player_id, 'id': unique_id,
                            'role': 'Player'}, ignore_index=True)

# Put this dataframe into Hasura database
insert_data_to_hasura(df)


