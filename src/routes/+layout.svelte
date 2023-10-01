<script>
	import '../app.postcss';
	import Sidebar from '$lib/SideBar.svelte';
	import Tabfeed from '$lib/TabFeed.svelte';
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
<footer>
	Copyright
</footer>
</main>

