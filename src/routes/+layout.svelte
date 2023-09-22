<script>
	import '../app.postcss';
	import Sidebar from '$lib/sidebar.svelte';
	import Tabfeed from '$lib/Tabfeed.svelte';
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

