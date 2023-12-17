import psycopg2
import requests
import pandas as pd
from tag_extractor import keyword_matching  # Import the function
import html2text

# Load the DataFrame from the pickle file
df = pd.read_pickle('club_players_data.pkl')

# Extract unique club and player names
unique_club_names = df['Club Name'].unique()
unique_player_names = df['Player Name'].unique()


def insert_tweet(cursor, user_id, username, content):
    # Convert HTML to plain text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    plain_text = text_maker.handle(content)

    tags = keyword_matching(plain_text, unique_club_names, unique_player_names)
    try:
        cursor.execute(
            "INSERT INTO tweets (user_id, username, content, tags, created_at) VALUES (%s, %s, %s, %s, NOW())",
            (user_id, username, plain_text, tags)
        )
    except psycopg2.DatabaseError as e:
        print(f"Error inserting tweet: {e}")
        # Handle error
        # You might want to handle this error more gracefully depending on your requirements

try:
    # PostgreSQL connection details
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5432/local")
    cursor = conn.cursor()

    # Fetch Mastodon user details
    cursor.execute("SELECT username, user_id FROM consolidated_mastodon")
    users = cursor.fetchall()

    # Base URL for fetching statuses
    base_url = 'https://mastodon.social/api/v1/accounts/'

    # Loop through the users and fetch their tweets
    for username, user_id in users:
        url = f"{base_url}{user_id}/statuses"
        response = requests.get(url)
        if response.status_code == 200:
            tweets = response.json()
            for tweet in tweets:
                # Check if the content is not blank
                if tweet['content'].strip():
                    insert_tweet(cursor, user_id, username, tweet['content'])
                    conn.commit()  # Commit after each insert
                else:
                    print(f"Skipped blank tweet for user {username}")
        else:
            print(f"Failed to fetch tweets for {username}. Status code: {response.status_code}")

except psycopg2.DatabaseError as e:
    print(f"Database error: {e}")
    conn.rollback()
except requests.RequestException as e:
    print(f"HTTP request error: {e}")
finally:
    if conn is not None:
        cursor.close()
        conn.close()
