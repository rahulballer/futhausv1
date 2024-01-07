import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests
import json
from dotenv import load_dotenv


# Load Hasura credentials from the .env file or environment
load_dotenv('/Users/rahulrangarajan/FootyBreak/futhaus/y/.env')
HASURA_GRAPHQL_ENDPOINT = os.getenv('VITE_HASURA_GRAPHQL_ENDPOINT')
HASURA_ADMIN_SECRET = os.getenv('VITE_HASURA_ADMIN_SECRET')

# Authenticate using the service account file
path_to_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')  # Ensure this environment variable is set
credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
gc = gspread.authorize(credentials)

# Open the Google Sheet and select the 'Club Tagging' tab
sheet_url = "https://docs.google.com/spreadsheets/d/1o68j_kwMarmDWj79UaS0KbQDzkz_C4EfE8LbDn6B8gc/edit#gid=1933161530"
worksheet = gc.open_by_url(sheet_url).worksheet('Club Tagging')

# Get all data from the worksheet
data = worksheet.get_all_values()

# Convert the data to a list of dictionaries (skip the first row if it's headers)
keys = data[0]  # Assuming first row is header
values = data[1:]  # Data rows
dict_list = [dict(zip(keys, row)) for row in values]

# GraphQL mutation template
mutation = """
mutation insertClubTagging($objects: [club_tagging_insert_input!]!) {
  insert_club_tagging(objects: $objects) {
    affected_rows
  }
}
"""

# Headers for Hasura GraphQL API
hasura_headers = {
    'Content-Type': 'application/json',
    'x-hasura-admin-secret': HASURA_ADMIN_SECRET  # Make sure this is set
}

# Make the request to Hasura
response = requests.post(
    HASURA_GRAPHQL_ENDPOINT, 
    json={'query': mutation, 'variables': {'objects': dict_list}},
    headers=hasura_headers
)

# Print the data being sent to Hasura for debugging purposes
print("Data being sent to Hasura:")
print(json.dumps({'query': mutation, 'variables': {'objects': dict_list}}, indent=4))

# Check response
if response.status_code == 200:
    print("Data uploaded successfully!")
    # Print the full response from Hasura
    print("Response from Hasura:")
    print(json.dumps(response.json(), indent=4))
else:
    print(f"Failed to upload data: {response.text}")
    # Print the full error response from Hasura
    print("Error Response from Hasura:")
    print(response.text)


