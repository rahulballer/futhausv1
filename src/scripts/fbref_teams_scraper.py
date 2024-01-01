import requests
from bs4 import BeautifulSoup
import re
import csv 


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

def get_team_logo_url(team_url):
    response = requests.get(team_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get full team name with fallback strategy
    full_team_name = get_full_team_name(team_url, soup)
    
    # Find the team logo URL
    logo_img = soup.find('img', {'class': 'teamlogo'})
    return full_team_name, logo_img['src'] if logo_img else None

def get_team_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    team_data = []
    for team_row in soup.find_all('tr'):
        team_cell = team_row.find('td', {'data-stat': 'team'})
        if team_cell:
            team_link = team_cell.find('a', href=True)
            if team_link:
                team_url = 'https://fbref.com' + team_link['href']
                team_name, team_logo_url = get_team_logo_url(team_url)
                team_data.append((team_name, team_url, team_logo_url))

    return team_data

team_data = get_team_data(main_url)
# Write the data to a CSV file
with open('teams.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(['team_name', 'team_url', 'team_logo_url'])
    # Write the team data
    for team in team_data:
        writer.writerow(team)

print("Data saved to teams.csv")
