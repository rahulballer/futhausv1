<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import {
    ApolloClient,
    InMemoryCache,
    HttpLink,
    split,
    gql
  } from '@apollo/client/core';
  import { WebSocketLink } from '@apollo/client/link/ws';
  import { getMainDefinition } from '@apollo/client/utilities';

  // Define your GraphQL endpoint and WebSocket endpoint
  const GRAPHQL_ENDPOINT = 'http://localhost:3000/graphql';
  const WS_ENDPOINT = 'ws://localhost:3000/graphql';

  // Type for a tweet
  interface Tweet {
    id: number;
    content: string;
    tags: string;
    user_id: string;
    username: string;
    created_at: string;
  }

  // Local store for tweets
  export const tweets = writable<Tweet[]>([]);

  // Apollo Client setup
  const httpLink = new HttpLink({ uri: GRAPHQL_ENDPOINT });
  const wsLink = new WebSocketLink({
    uri: WS_ENDPOINT,
    options: {
      reconnect: true
    }
  });

  const link = split(
    ({ query }) => {
      const definition = getMainDefinition(query);
      return (
        definition.kind === 'OperationDefinition' &&
        definition.operation === 'subscription'
      );
    },
    wsLink,
    httpLink
  );

  const client = new ApolloClient({
    link,
    cache: new InMemoryCache()
  });

  // GraphQL subscription for tweets
  const TWEETS_SUBSCRIPTION = gql`
    subscription {
      tweetAdded {
        id
        content
        tags
        user_id
        username
        created_at
      }
    }
  `;

  // GraphQL query for existing tweets
  const FETCH_TWEETS_QUERY = gql`
    query {
      tweets {
        id
        content
        tags
        user_id
        username
        created_at
      }
    }
  `;

// Function to fetch existing tweets and sort them
async function fetchTweets() {
  try {
    const { data } = await client.query({ query: FETCH_TWEETS_QUERY });
    if (data && data.tweets) {
      // Sort tweets by created_at date in descending order (newest first)
      const sortedTweets = data.tweets.slice().sort((a: Tweet, b: Tweet) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      tweets.set(sortedTweets);
    }
  } catch (error) {
    console.error('Error fetching existing tweets:', error);
  }
}


  // Subscribe to new tweets
  function subscribeToTweets() {
    console.log('Preparing to subscribe to tweets...');
    client.subscribe({ query: TWEETS_SUBSCRIPTION })
      .subscribe({
        next(response) {
          console.log('New tweet data received:', response);
          if (!response.data || !response.data.tweetAdded) {
            console.error('Received data is not in the expected format:', response.data);
            return;
          }
          tweets.update(currentTweets => {
            console.log('Updating store with new tweets');
            return [...currentTweets, response.data.tweetAdded];
          });
        },
        error(err) {
          console.error('Error during subscription:', err);
        },
        complete() {
          console.log('Subscription completed');
        }
      });
  }

// Call fetchTweets inside onMount to load tweets when the component mounts
onMount(() => {
  console.log('Component mounted, fetching tweets...');
  fetchTweets();
  subscribeToTweets();
});

</script>

<section>
  <div>
    {#each $tweets as tweet (tweet.id)}
      <article>
        <h2>{tweet.username} - {new Date(tweet.created_at).toLocaleString()}</h2>
        <p>{tweet.content}</p> 
        <p>{tweet.tags}</p>
      </article>
    {/each}
  </div>
</section>
