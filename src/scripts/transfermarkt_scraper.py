import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd

def scrape_page(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    clubs = soup.select('td.no-border-links.hauptlink a')
    page_data = []

    for club in clubs:
        club_name = club.get_text().strip()
        club_url = 'https://www.transfermarkt.com' + club['href']

        club_response = requests.get(club_url, headers={'User-Agent': 'Mozilla/5.0'})
        club_soup = BeautifulSoup(club_response.content, 'html.parser')

        country = club_soup.select_one('img.flaggenrahmen')['title'] if club_soup.select_one('img.flaggenrahmen') else 'N/A'

        # Extracting team avatar
        team_avatar_elem = club_soup.select_one('img[src*="images/wappen/head"]')
        team_avatar = team_avatar_elem['src'] if team_avatar_elem else 'N/A'

        # Extracting league information
        league_elem = club_soup.select_one('a[href*="/startseite/wettbewerb"]')
        league = league_elem.get_text().strip() if league_elem else 'N/A'
        league_url = 'https://www.transfermarkt.com' + league_elem['href'] if league_elem else 'N/A'

        # Extracting league avatar
        league_avatar_elem = club_soup.select_one('img[srcset*="images/logo/homepageWappen150x150"]')
        league_avatar = league_avatar_elem['srcset'].split(',')[1].split('?')[0].strip() if league_avatar_elem else 'N/A'

        players = club_soup.select('td.hauptlink a')
        for player in players:
            player_name = player.get_text().strip()
            if not re.search(r'\d', player_name):
                player_url = 'https://www.transfermarkt.com' + player['href']
                if 'spieler' in player_url:
                    # Extracting player avatar
                    player_response = requests.get(player_url, headers={'User-Agent': 'Mozilla/5.0'})
                    player_soup = BeautifulSoup(player_response.content, 'html.parser')
                    player_avatar_elem = player_soup.select_one('img[src*="portrait/header"]')
                    player_avatar = player_avatar_elem['src'] if player_avatar_elem else 'N/A'

                    page_data.append([club_name, country, club_url, team_avatar, league, league_url, league_avatar, player_name, player_url, player_avatar])

    return page_data

main_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstemannschaften/marktwertetop"
club_data = []

# Determine the number of pages to scrape
number_of_pages = 10  # Replace with actual number of pages

for page_number in range(1, number_of_pages + 1):
    page_url = f"{main_url}?ajax=yw1&page={page_number}"
    club_data.extend(scrape_page(page_url))

# Write data to CSV
with open('club_players_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Club Name', 'Country', 'Club URL', 'Team Avatar', 'League', 'League URL', 'League Avatar', 'Player Name', 'Player URL', 'Player Avatar'])  # Header
    writer.writerows(club_data)

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(club_data, columns=['Club Name', 'Country', 'Club URL', 'Team Avatar', 'League', 'League URL', 'League Avatar', 'Player Name', 'Player URL', 'Player Avatar'])

# Save the DataFrame as a pickle file
df.to_pickle('club_players_data.pkl')
