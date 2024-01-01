import os
import requests
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
df = pd.DataFrame(columns=['League', 'League URL', 'League Avatar', 'Club', 'Club URL', 'Club Avatar', 'Person', 'Person URL', 'Person Avatar', 'Person Country', 'Role'])

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

        if manager:
            manager_avatar_url = f'{base_api_url}manager/{manager.get("id", "")}/image'
            manager_url = f'https://www.sofascore.com/manager/{manager.get("slug", "")}/{manager.get("id", "")}'
            manager_country = manager.get('country', {}).get('name', '')
            df = df._append({'League': league_name, 'League URL': league_url, 'League Avatar': league_avatar_url,
                            'Club': team['name'], 'Club URL': club_url, 'Club Avatar': club_avatar_url, 
                            'Person': manager.get('name', ''), 'Person URL': manager_url, 
                            'Person Avatar': manager_avatar_url, 'Person Country': manager_country, 
                            'Role': 'Manager'}, ignore_index=True)

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
            df = df._append({'League': league_name, 'League URL': league_url, 'League Avatar': league_avatar_url,
                            'Club': team['name'], 'Club URL': club_url, 'Club Avatar': club_avatar_url, 
                            'Person': player_name, 'Person URL': player_url, 
                            'Person Avatar': player_avatar_url, 'Person Country': player_country, 
                            'Role': 'Player'}, ignore_index=True)

# Use the JSON file you downloaded from Google Cloud Console
# Use the environment variable for the JSON file
path_to_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


# Authenticate using the service account file
credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
gc = gspread.authorize(credentials)

# Open the Google Sheet using its URL
sheet_url = "https://docs.google.com/spreadsheets/d/1o68j_kwMarmDWj79UaS0KbQDzkz_C4EfE8LbDn6B8gc/edit#gid=1933161530"
sheet = gc.open_by_url(sheet_url)

# Select the first sheet
worksheet = sheet.worksheet('Club Tagging')  # Replace with the actual title


# Get the existing data from the first column
existing_clubs = worksheet.col_values(1)

# Get the unique clubs from the DataFrame
unique_clubs = df['Club'].unique()

# Append new clubs that are not in the existing_clubs
new_clubs = [club for club in unique_clubs if club not in existing_clubs]

# Update the Google Sheet with new clubs
for club in new_clubs:
    worksheet.append_row([club])
