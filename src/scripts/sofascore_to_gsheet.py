import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import pandas as pd
import os
from dotenv import load_dotenv


# Load Hasura credentials from the .env file or environment
load_dotenv('/Users/rahulrangarajan/FootyBreak/futhaus/y/.env')
HASURA_GRAPHQL_ENDPOINT = os.getenv('VITE_HASURA_GRAPHQL_ENDPOINT')
HASURA_ADMIN_SECRET = os.getenv('VITE_HASURA_ADMIN_SECRET')

# GraphQL query to fetch data from Hasura
query = """
{
  sofascore {
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
"""

# Headers for Hasura GraphQL API
headers = {
    'Content-Type': 'application/json',
    'x-hasura-admin-secret': HASURA_ADMIN_SECRET
}

# Make the request to Hasura
response = requests.post(
    HASURA_GRAPHQL_ENDPOINT, 
    json={'query': query},
    headers=headers
)

# Check for errors
if response.status_code == 200:
    data = response.json()
    # Convert the response data to DataFrame
    df = pd.DataFrame(data['data']['sofascore'])
else:
    print(f"Failed to fetch data: {response.text}")
    df = pd.DataFrame()  # Empty DataFrame in case of failure

# Now df contains the data from your Hasura table

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
unique_clubs = df['club'].unique()

# Append new clubs that are not in the existing_clubs
new_clubs = [club for club in unique_clubs if club not in existing_clubs]

# Update the Google Sheet with new clubs
for club in new_clubs:
    worksheet.append_row([club])