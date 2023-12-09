import psycopg2
import requests

def insert_tweet(cursor, user_id, username, content):
    try:
        cursor.execute(
            "INSERT INTO tweets (user_id, username, content, created_at) VALUES (%s, %s, %s, NOW())",
            (user_id, username, content)
        )
    except psycopg2.DatabaseError as e:
        print(f"Error inserting tweet: {e}")
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
                insert_tweet(cursor, user_id, username, tweet['content'])
                conn.commit()  # Commit after each insert
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
