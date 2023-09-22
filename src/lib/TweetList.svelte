<script lang="ts">
    export let tweets: { content: string }[] = [];
  </script>
  
  <ul>
    {#each tweets as tweet}
      <li>{tweet.content}</li>
    {/each}
  </ul>