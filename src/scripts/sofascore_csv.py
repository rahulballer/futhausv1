import requests
import csv
import re

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
}

headers['If-Modified-Since'] = 'Thu, 01 Jan 2023 00:00:00 GMT'


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
    'https://www.sofascore.com/tournament/football/germany/2-bundesliga/44': '52607', #2. bundesliga
    'https://www.sofascore.com/tournament/football/england/championship/18': '52367', #championship
    'https://www.sofascore.com/tournament/football/spain/laliga-2/54': '52563', #la liga 2
    'https://www.sofascore.com/tournament/football/italy/serie-b/53': '52947', #serie b
    'https://www.sofascore.com/tournament/football/france/ligue-2/182': '52572', #ligue 2

    
}

# Base API URL
base_api_url = 'https://api.sofascore.com/api/v1/'

# CSV file setup
csv_file = open('sofascore_data.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.DictWriter(csv_file, fieldnames=['League', 'League URL', 'League Avatar', 'Club', 'Club URL', 'Club Avatar', 'Person', 'Person URL', 'Person Avatar', 'Person Country', 'Role'])
csv_writer.writeheader()

# Process each league
for league_url, season_id in leagues.items():
    league_id = re.search(r'/(\d+)$', league_url).group(1)
    league_avatar_url = f'{base_api_url}unique-tournament/{league_id}/image/dark'
    standings_url = f'{base_api_url}unique-tournament/{league_id}/season/{season_id}/standings/total'

    standings_data = fetch_json(standings_url, headers)
    if not standings_data or 'standings' not in standings_data:
        continue  # Skip to next league if data is missing

    # Get the league name from the JSON
    league_name = standings_data['standings'][0]['tournament']['name']

    # Extract league, team, and player data
    for team_data in standings_data['standings'][0]['rows']:
        team = team_data['team']
        club_avatar_url = f'{base_api_url}team/{team["id"]}/image'
        club_url = f'https://www.sofascore.com/team/football/{team["slug"]}/{team["id"]}'

        # Fetch team details for manager info
        team_details_url = f'{base_api_url}team/{team["id"]}'
        team_details = fetch_json(team_details_url, headers)
        manager = team_details['team'].get('manager', {})
        if manager:
            manager_avatar_url = f'{base_api_url}manager/{manager.get("id", "")}/image'
            manager_url = f'https://www.sofascore.com/manager/{manager.get("slug", "")}/{manager.get("id", "")}'
            manager_country = manager.get('country', {}).get('name', '')

            # Write manager data to CSV
            csv_writer.writerow({
                'League': league_name,
                'League URL': league_url,
                'League Avatar': league_avatar_url,
                'Club': team['name'],
                'Club URL': club_url,
                'Club Avatar': club_avatar_url,
                'Person': manager.get('name', ''),
                'Person URL': manager_url,
                'Person Avatar': manager_avatar_url,
                'Person Country': manager_country,
                'Role': 'Manager'
            })

        # Fetch players for the team
        players_url = f'{base_api_url}team/{team["id"]}/players'
        players_data = fetch_json(players_url, headers)
        if not players_data:
            continue  # Skip to next team if player data is missing

        # Track player names to avoid duplicates
        player_names = set()

        for player_info in players_data['players']:
            player = player_info['player']
            player_name = player['name']

            # Skip if player is already processed for this team
            if player_name in player_names:
                continue

            player_names.add(player_name)
            player_id = player['id']
            player_avatar_url = f'{base_api_url}player/{player_id}/image'
            player_url = f'https://www.sofascore.com/player/{player["slug"]}/{player_id}'
            player_country = player.get('country', {}).get('name', '')

            # Write player data to CSV
            csv_writer.writerow({
                'League': league_name,
                'League URL': league_url,
                'League Avatar': league_avatar_url,
                'Club': team['name'],
                'Club URL': club_url,
                'Club Avatar': club_avatar_url,
                'Person': player_name,
                'Person URL': player_url,
                'Person Avatar': player_avatar_url,
                'Person Country': player_country,
                'Role': 'Player'
            })

# Close the CSV file
csv_file.close()