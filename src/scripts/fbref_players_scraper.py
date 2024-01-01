import requests
from bs4 import BeautifulSoup
import re
import time

# URL of the main page
main_url = 'https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats'

# Updated headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'keep-alive'
}

def get_request(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {url}, Error: {e}")
        time.sleep(5)  # wait before retrying
        return None

def get_full_team_name(url, soup):
    match = re.search(r'/squads/\w+/([\w-]+)-Stats', url)
    if match:
        return match.group(1).replace('-', ' ')

    header = soup.find('h1')
    if header:
        return header.get_text().strip()

    return ''

def get_team_data(url):
    response = get_request(url)
    if not response:
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    team_data = []

    for team_row in soup.find_all('tr'):
        team_cell = team_row.find('td', {'data-stat': 'team'})
        if team_cell:
            team_link = team_cell.find('a', href=True)
            if team_link:
                team_url = 'https://fbref.com' + team_link['href']
                team_response = get_request(team_url)
                if not team_response:
                    continue
                team_soup = BeautifulSoup(team_response.content, 'html.parser')
                team_name = get_full_team_name(team_url, team_soup)
                team_data.append((team_name, team_url))

    return team_data

def get_current_team(soup):
    team_link = soup.find('a', href=lambda x: x and x.endswith('-Stats'))
    if team_link:
        url_path = team_link['href']
        # Extract everything after the last "/" and before "-Stats"
        team_name_segment = url_path.rsplit('/', 1)[-1].split('-Stats')[0]
        # Replace hyphens with spaces to form the complete team name
        team_name = team_name_segment.replace('-', ' ')
        print(team_name)
        return team_name
    return None

def get_player_data(team_url, team_name):
    response = get_request(team_url)
    if not response:
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    player_data = []
    seen_players = set()

    for player_row in soup.find_all('tr'):
        player_cell = player_row.find('th', {'data-stat': 'player'})
        if player_cell:
            player_link = player_cell.find('a', href=True)
            if player_link and player_link['href'] not in seen_players:
                player_url = 'https://fbref.com' + player_link['href']
                player_response = get_request(player_url)
                if not player_response:
                    continue
                player_soup = BeautifulSoup(player_response.content, 'html.parser')
                current_team = get_current_team(player_url, player_soup)
                if current_team and current_team == team_name:
                    player_name = player_link.text.strip()
                    player_avatar = get_player_avatar(player_url)
                    player_data.append((player_name, player_url, player_avatar))
                seen_players.add(player_link['href'])

    return player_data

def get_player_avatar(player_url):
    response = get_request(player_url)
    if not response:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    avatar_img = soup.find('img', alt=lambda x: x and x.endswith('headshot'))
    return avatar_img['src'] if avatar_img else None

# Get team data from the main URL
team_data = get_team_data(main_url)

# For each team, get player data
for team_name, team_url in team_data[:3]:  # Limit to first 3 teams for testing
    print(f"Team: {team_name}")
    player_data = get_player_data(team_url, team_name)
    for player_name, player_url, player_avatar in player_data:
        print(f"Player: {player_name}, URL: {player_url}, Avatar: {player_avatar}")