<script lang="ts">
    import { onMount } from 'svelte';
    import { subscribeToTweetsStream, tweets } from '$lib/graphql-ws-client';
  
    onMount(() => {
      subscribeToTweetsStream();
    });
  </script>
  
  {#each $tweets as tweet}
    <div>
      <p>{tweet.username}</p>
      <p>{tweet.created_at}</p>
      <p>{tweet.content}</p>
      <p>{tweet.tags}</p>
      <!-- Add more tweet details as needed -->
    </div>
  {/each}
  