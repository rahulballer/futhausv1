import requests
from bs4 import BeautifulSoup
import pandas as pd

main_url = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"
response = requests.get(main_url, headers={'User-Agent': 'Mozilla/5.0'})
main_soup = BeautifulSoup(response.content, 'html.parser')

teams = main_soup.select('a[href*="/en/squads/"]')
team_data = []

for team in teams:
    team_name = team.get_text().strip()
    team_url = 'https://fbref.com' + team['href']

    team_response = requests.get(team_url, headers={'User-Agent': 'Mozilla/5.0'})
    team_soup = BeautifulSoup(team_response.content, 'html.parser')

    players = team_soup.select('a[href*="/en/players/"]')
    for player in players:
        player_name = player.get_text().strip()
        player_url = 'https://fbref.com' + player['href']
        team_data.append([team_name, player_name, player_url])

# Create DataFrame
df = pd.DataFrame(team_data, columns=['Team Name', 'Player Name', 'Player URL'])

# Display the DataFrame
print(df)