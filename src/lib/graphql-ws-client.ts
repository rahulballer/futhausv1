// src/lib/graphql-ws-client.ts
import { createClient } from 'graphql-ws';
import type { Client } from 'graphql-ws';
import { BehaviorSubject } from 'rxjs';

const HASURA_ADMIN_SECRET = import.meta.env.VITE_HASURA_ADMIN_SECRET;

interface Tweet {
  id: number;
  content: string;
  tags: string;
  user_id: string;
  username: string;
  created_at: string;
}

type GraphQLClient = Client | { subscribe: (options: any) => { unsubscribe: () => void } };

const isBrowser = typeof window !== 'undefined';

let client: GraphQLClient;
if (isBrowser) {
  client = createClient({
    url: 'wss://local.hasura.nhost.run/v1/graphql',
    connectionParams: {
      headers: {
        'x-hasura-admin-secret': HASURA_ADMIN_SECRET,
      },
    },
  });
} else {
  client = { subscribe: () => ({ unsubscribe: () => {} }) };
}

export const tweets = new BehaviorSubject<Tweet[]>([]);

export function subscribeToTweetsStream() {
  if (!isBrowser) return;

  // Adjust the subscription query to remove the batch logic if any
  const subscriptionQuery = `
    subscription GetTweetsSubscription {
      tweets {
        id
        content
        tags
        user_id
        username
        created_at
      }
    }`;

  client.subscribe({ query: subscriptionQuery }, {
    next: (data: any) => {
      if (data.data) {
        // Here you might want to append new tweets to the existing ones
        // This assumes your subscription is only sending new tweets
        tweets.next([...tweets.getValue(), ...data.data.tweets]);
      }
    },
    error: (err: Error) => console.error('Subscription error:', err),
    complete: () => console.log('Subscription complete'),
  });
}
