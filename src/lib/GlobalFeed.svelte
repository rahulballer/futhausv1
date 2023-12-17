<script lang="ts">
    import { onMount } from 'svelte';
    import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client/core';
    import { WebSocketLink } from '@apollo/client/link/ws';
    import { getMainDefinition } from '@apollo/client/utilities';
    import { writable } from 'svelte/store';
    import { gql } from 'graphql-tag';
  
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
  
    console.log('Environment Variables:');
    console.log('GraphQL Endpoint:', import.meta.env.VITE_HASURA_GRAPHQL_ENDPOINT);
    console.log('Admin Secret:', import.meta.env.VITE_HASURA_ADMIN_SECRET);
    console.log('WebSocket Endpoint:', import.meta.env.VITE_HASURA_WS_ENDPOINT);
  
    // Create an HTTP link to the GraphQL API
    const httpLink = new HttpLink({
      uri: import.meta.env.VITE_HASURA_GRAPHQL_ENDPOINT,
      headers: {
        'x-hasura-admin-secret': import.meta.env.VITE_HASURA_ADMIN_SECRET,
      },
    });
  
    // Create a WebSocket link
    const wsLink = new WebSocketLink({
      uri: import.meta.env.VITE_HASURA_WS_ENDPOINT,
      options: {
        reconnect: true,
        connectionParams: {
          headers: {
            'x-hasura-admin-secret': import.meta.env.VITE_HASURA_ADMIN_SECRET,
          },
        },
      },
    });
  
    // Using the split function to route queries to the proper link
    const link = split(
      ({ query }) => {
        const definition = getMainDefinition(query);
        return (
          definition.kind === 'OperationDefinition' &&
          definition.operation === 'subscription'
        );
      },
      wsLink,
      httpLink,
    );
  
    // Initialize Apollo Client
    const client = new ApolloClient({
      link,
      cache: new InMemoryCache()
    });
  
    // GraphQL subscription for tweets
    const TWEETS_SUBSCRIPTION = gql`
      subscription GetTweetsStreamingSubscription {
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
  
    // Function to start the tweets subscription
    function subscribeToTweets() {
      client.subscribe({
        query: TWEETS_SUBSCRIPTION,
      }).subscribe({
        next(response) {
          console.log('New data received:', response.data);
          tweets.update(currentTweets => {
            return [...currentTweets, ...response.data.tweets];
          });
        },
        error(err) {
          console.error('Error subscribing to tweets:', err);
        }
      });
    }
  
    onMount(() => {
      subscribeToTweets();
    });
  </script>
  
  {#each $tweets as tweet}
    <div>
      <p>{tweet.username}</p>
      <p>{tweet.created_at}</p>
      <p>{tweet.content}</p>
      <p>{tweet.tags}</p>
    </div>
  {/each}
  