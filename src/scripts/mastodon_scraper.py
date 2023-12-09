import requests

# Dictionary mapping user handles to their respective IDs
user_ids = {
    '@fabrizioromano': '109757081274941020',
    # Add more accounts here, e.g., '@anotheruser': 'their_id'
}

# Base URL for fetching statuses
base_url = 'https://mastodon.social/api/v1/accounts/'

# Loop through the dictionary
for user_handle, user_id in user_ids.items():
    # Construct the full URL for each user
    url = f"{base_url}{user_id}/statuses"

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        toots = response.json()

        # Print the user handle and the content of each toot
        print(f"Toots for {user_handle}:")
        for toot in toots:
            print(toot['content'])
        print("\n")  # New line for better readability between users
    else:
        print(f"Failed to fetch toots for {user_handle}. Status code: {response.status_code}")
