import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd

# Function to scrape a single page
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
        players = club_soup.select('td.hauptlink a')

        for player in players:
            player_name = player.get_text().strip()
            if not re.search(r'\d', player_name):
                player_url = 'https://www.transfermarkt.com' + player['href']
                if 'spieler' in player_url:
                    page_data.append([club_name, country, club_url, player_name, player_url])

    return page_data

main_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstemannschaften/marktwertetop"
club_data = []

# Determine the number of pages to scrape
number_of_pages = 10  # Replace with actual number of pages

# Iterate through all pages
for page_number in range(1, number_of_pages + 1):
    page_url = f"{main_url}?ajax=yw1&page={page_number}"
    club_data.extend(scrape_page(page_url))

# Write data to CSV
with open('club_players_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Club Name', 'Country', 'Club URL', 'Player Name', 'Player URL'])  # Header
    writer.writerows(club_data)

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(club_data, columns=['Club Name', 'Country', 'Club URL', 'Player Name', 'Player URL'])

# Save the DataFrame as a pickle file
df.to_pickle('club_players_data.pkl')
