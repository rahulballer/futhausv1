<script>
	import '../app.postcss';
	import Sidebar from '$lib/sidebar.svelte';
</script>

<style>
	main {
		display: flex;
	}
</style>


<main>
<Sidebar />
<slot />
<footer>
	Copyright
</footer>
</main>

