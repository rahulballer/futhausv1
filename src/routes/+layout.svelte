<script>
	import '../app.postcss';
	import Sidebar from '$lib/sidebar.svelte';
	import Tabfeed from '$lib/Tabfeed.svelte';
	import TweetTable from '$lib/TweetTable.svelte';
</script>

<style>
	main {
		display: flex;
	}
</style>


<main>
<Sidebar />
<slot />
<Tabfeed />
<TweetTable />
<footer>
	Copyright
</footer>
</main>

