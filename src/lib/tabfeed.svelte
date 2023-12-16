<script lang="ts">
  import {
    Tab,
    TabGroup,
    TabList,
    TabPanel,
    TabPanels,
  } from "@rgossiaux/svelte-headlessui";

  import GlobalFeed from './GlobalFeed.svelte';
</script>

<TabGroup>
  <TabList>
    <Tab class={({selected}) => selected ? "tab-selected" : "tab-unselected"}>Personal</Tab>
    <Tab class={({selected}) => selected ? "tab-selected" : "tab-unselected"}>Social</Tab>
    <Tab class={({selected}) => selected ? "tab-selected" : "tab-unselected"}>Global</Tab>
    <Tab class={({selected}) => selected ? "tab-selected" : "tab-unselected"}>Trending</Tab>
  </TabList>
  <TabPanels>
    <TabPanel class="tab-panel">Personal Content</TabPanel>
    <TabPanel class="tab-panel">Social Content</TabPanel>
    <TabPanel class="tab-panel"><GlobalFeed /></TabPanel>
    <TabPanel class="tab-panel">Trending Content</TabPanel>
  </TabPanels>
</TabGroup>

  
  <style>
    /* WARNING: This is just for demonstration.
        Using :global() in this way can be risky. */
    :global(.tab-selected) {
      background-color: rgb(59 130 246);
      color: rgb(255 255 255);
    }
  
    :global(.tab-unselected) {
      background-color: rgb(255 255 255);
      color: rgb(0 0 0);
    }

    :global(.tab-panel) {
        font-size: 12px;
        font-family: Arial, sans-serif;
        color:white;
    }

  </style>
  
