import dotenv from 'dotenv';
import express from 'express';
import { createServer } from 'http';
import { GraphQLClient } from 'graphql-request';
import { makeExecutableSchema } from '@graphql-tools/schema';
import { SubscriptionServer } from 'subscriptions-transport-ws';
import { execute, subscribe } from 'graphql';
import { ApolloServer, gql } from 'apollo-server-express';
import { PubSub } from 'graphql-subscriptions';

// Initialize environment variables
dotenv.config({ path: '/Users/rahulrangarajan/FootyBreak/futhaus/y/.env' });

// Load environment variables
const {
  VITE_HASURA_GRAPHQL_ENDPOINT,
  VITE_HASURA_ADMIN_SECRET
} = process.env;

// Initialize a PubSub instance
const pubsub = new PubSub();
const TWEETS_TOPIC = 'NEW_TWEET';

// Define your type definitions using gql
const typeDefs = gql`
  type Tweet {
    id: Int
    content: String
    tags: String
    user_id: String
    username: String
    created_at: String
    media_attachments: String
    avatar: String
  }

  type Query {
    tweets: [Tweet]
  }

  type Subscription {
    tweetAdded: Tweet
  }
`;

// Define the GraphQLClient
const client = new GraphQLClient(VITE_HASURA_GRAPHQL_ENDPOINT, {
  headers: {
    'x-hasura-admin-secret': VITE_HASURA_ADMIN_SECRET,
  },
});

// Provide resolver functions for your schema fields
const resolvers = {
  Query: {
    tweets: async () => {
      const query = `query GetTweets {
        tweets {
          id
          content
          tags
          user_id
          username
          created_at
          media_attachments
          avatar
        }
      }`;
      try {
        const response = await client.request(query);
        return response.tweets;
      } catch (error) {
        console.error('Error fetching tweets:', error);
        throw new Error('Failed to fetch tweets.');
      }
    },
  },
  Subscription: {
    tweetAdded: {
      subscribe: () => pubsub.asyncIterator([TWEETS_TOPIC])
    },
  },
};

// Create the GraphQL schema
const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

// Set up Apollo Server
const server = new ApolloServer({
  schema,
  plugins: [{
    async serverWillStart() {
      return {
        async drainServer() {
          subscriptionServer.close();
        }
      };
    }
  }],
});

// Function to simulate a new tweet event
function onNewTweet(newTweet) {
  pubsub.publish(TWEETS_TOPIC, { tweetAdded: newTweet });
}

// Start Apollo Server and set up WebSocket server for subscriptions
(async function startApolloServer() {
  await server.start();
  server.applyMiddleware({ app });

  const PORT = process.env.PORT || 3000;
  httpServer.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}${server.graphqlPath}`);

    const subscriptionServer = SubscriptionServer.create({
      schema,
      execute,
      subscribe,
      onConnect(connectionParams, webSocket, context) {
        console.log('Connected to websocket');
      },
      onDisconnect(webSocket, context) {
        console.log('Disconnected from websocket');
      },
    }, {
      server: httpServer,
      path: server.graphqlPath,
    });

    // Simulate a new tweet event 5 seconds after the server starts
    setTimeout(() => {
      onNewTweet({
        id: Date.now(),
        content: "Hello, this is a test tweet!",
        tags: "test",
        user_id: "1",
        username: "testuser",
        created_at: new Date().toISOString()
      });
      console.log("Test tweet published!");
    }, 5000);
  });
})();
