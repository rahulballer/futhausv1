import WebSocket from 'ws';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import { htmlToText } from 'html-to-text';

dotenv.config({ path: '/Users/rahulrangarajan/FootyBreak/futhaus/y/.env' });

const ws = new WebSocket(`wss://streaming.mastodon.social/api/v1/streaming?stream=user&access_token=${process.env.MASTODON_ACCESS_TOKEN}`);

ws.on('message', async (data) => {
  const event = JSON.parse(data);

  if (event.event === 'update') {
    const status = JSON.parse(event.payload);
    let plainTextContent = htmlToText(status.content, { wordwrap: 130 });

    // Convert Mastodon social tags to hashtags and clean up HTML
    plainTextContent = plainTextContent.replace(/<a href="https:\/\/mastodon.social\/tags\/([^"]+)">[^<]+<\/a>/g, '#$1');
    plainTextContent = plainTextContent.replace(/<[^>]+>/g, '');

    // Replace bracketed URLs with hyperlink
    plainTextContent = plainTextContent.replace(/\[https?:\/\/[^\]]+\]/g, '');

    console.log('New status:', plainTextContent);

    // Prepare the data for the mutation
    const tweetData = {
      user_id: status.account.id,
      username: status.account.username,
      avatar: status.account.avatar,
      content: plainTextContent,
      created_at: status.created_at,
      media_attachments: status.media_attachments.map(attachment => attachment.url).join(','),
      source: 'twitter'
    };

    // Construct the GraphQL mutation
    const mutation = `
      mutation InsertTweet($tweet: tweets_insert_input!) {
        insert_tweets_one(object: $tweet) {
          id
        }
      }
    `;

    // Send the mutation to Hasura
    try {
      const response = await fetch(process.env.VITE_HASURA_GRAPHQL_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-hasura-admin-secret': process.env.VITE_HASURA_ADMIN_SECRET,
        },
        body: JSON.stringify({
          query: mutation,
          variables: { tweet: tweetData }
        }),
      });

      const responseData = await response.json();
      console.log('Inserted data:', responseData);
    } catch (error) {
      console.error('Error inserting data to Hasura:', error);
    }
  }
});

ws.on('open', () => {
  console.log('Connected to Mastodon stream');
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
});

ws.on('close', () => {
  console.log('Disconnected from Mastodon stream');
  // Optionally implement reconnection logic here
});
