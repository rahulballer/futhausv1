require('dotenv').config();
const { ApolloServer, gql } = require('apollo-server-express');
const express = require('express');
const { createServer } = require('http');
const { GraphQLClient } = require('graphql-request');
const { WebSocket } = require('ws');
const { makeExecutableSchema } = require('@graphql-tools/schema');

// Check environment variables
console.log('Hasura GraphQL Endpoint:', process.env.VITE_HASURA_GRAPHQL_ENDPOINT);
console.log('Hasura Admin Secret:', process.env.VITE_HASURA_ADMIN_SECRET);
console.log('Hasura WebSocket Endpoint:', process.env.VITE_HASURA_WS_ENDPOINT);

// GraphQL client for making requests to Hasura
const client = new GraphQLClient(process.env.VITE_HASURA_GRAPHQL_ENDPOINT, {
  headers: {
    'x-hasura-admin-secret': process.env.VITE_HASURA_ADMIN_SECRET,
  },
});

// GraphQL schema definitions
const typeDefs = gql`
  type Tweet {
    id: Int
    content: String
    tags: String
    user_id: String
    username: String
    created_at: String
  }

  type Query {
    tweets: [Tweet]
  }

  type Subscription {
    tweets: [Tweet]
  }
`;

// Resolvers for the defined schema
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
    tweets: {
      subscribe: () => {
        throw new Error('Real-time subscriptions are not yet supported in this setup.');
      },
    },
  },
};

// Create an executable schema
const schema = makeExecutableSchema({ typeDefs, resolvers });

// Express application setup
const app = express();
const httpServer = createServer(app);

// Apollo Server setup
const server = new ApolloServer({
  schema,
  plugins: [
    {
      async serverWillStart() {
        return {
          async drainServer() {
            // Close the server when shutting down
          },
        };
      },
    },
  ],
});

// Start the server and apply middleware
server.start().then(() => {
  server.applyMiddleware({ app });

  // Define the server port
  const PORT = process.env.PORT || 3000;

  // Start listening on the port
  httpServer.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}${server.graphqlPath}`);
  });
});

// WebSocket client to connect to Hasura's real-time updates
const wsClient = new WebSocket(process.env.VITE_HASURA_WS_ENDPOINT, ['graphql-ws'], {
  headers: {
    'x-hasura-admin-secret': process.env.VITE_HASURA_ADMIN_SECRET,
  },
});

wsClient.onopen = () => {
  console.log('WebSocket Client Connected');
  wsClient.send(JSON.stringify({
    type: 'connection_init',
    payload: {},
  }));
};

wsClient.onmessage = (message) => {
  const data = JSON.parse(message.data);

  // Handle different types of messages
  if (data.type === 'connection_ack') {
    console.log('Connection acknowledged');
  } else if (data.type === 'data') {
    console.log('Data received:', data.payload);
  } else if (data.type === 'error') {
    console.error('Error message received:', data.payload);
  } else if (data.type === 'ka') {
    // Keep Alive message, no action needed
  } else {
    console.log('Received unknown message type:', data);
  }
};

wsClient.onerror = (error) => {
  console.error('WebSocket Error:', error);
};
