import requests
from bs4 import BeautifulSoup
import re

# URL of the main page
main_url = 'https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats'

def get_full_team_name(url, soup):
    # Enhanced pattern matching to capture team names
    match = re.search(r'/squads/\w+/([\w-]+)-Stats', url)
    if match:
        return match.group(1).replace('-', ' ')

    # Fallback: Extract team name from the page content if pattern matching fails
    header = soup.find('h1')
    if header:
        return header.get_text().strip()

    return ''

def get_league_data(team_soup):
    league_link = team_soup.find('a', href=re.compile(r'/en/comps/\d+/[\w-]+-Stats'))
    if league_link:
        league_name = league_link.text
        league_url = 'https://fbref.com' + league_link['href']
        league_avatar = get_league_avatar(league_url)
        return league_name, league_url, league_avatar
    return '', '', ''

def get_league_avatar(league_url):
    response = requests.get(league_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    league_logo = soup.find('img', class_='teamlogo')
    if league_logo:
        return league_logo['src']
    return None

def get_team_and_league_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    for team_row in soup.find_all('tr'):
        team_cell = team_row.find('td', {'data-stat': 'team'})
        if team_cell:
            team_link = team_cell.find('a', href=True)
            if team_link:
                team_url = 'https://fbref.com' + team_link['href']
                team_response = requests.get(team_url)
                team_soup = BeautifulSoup(team_response.content, 'html.parser')
                
                team_name = get_full_team_name(team_url, team_soup)
                league_name, league_url, league_avatar = get_league_data(team_soup)

                data.append((team_name, team_url, league_name, league_url, league_avatar))

    return data

team_and_league_data = get_team_and_league_data(main_url)
for item in team_and_league_data:
    print(f"Team: {item[0]}, Team URL: {item[1]}, League: {item[2]}, League URL: {item[3]}, League Avatar: {item[4]}")
