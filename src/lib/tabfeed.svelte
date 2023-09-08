<script>
    import {
      Tab,
      TabGroup,
      TabList,
      TabPanel,
      TabPanels,
    } from "@rgossiaux/svelte-headlessui";
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
      <TabPanel class="tab-panel">Global Content</TabPanel>
      <TabPanel class="tab-panel">Trending Content</TabPanel>
    </TabPanels>
  </TabGroup>

  
  <style>
    /* WARNING: This is just for demonstration.
        Using :global() in this way can be risky. */
    :global(.tab-selected) {
      background-color: rgb(3, 83, 243);
      color: rgb(255 255 255);
    }
  
    :global(.tab-unselected) {
      background-color: rgb(145, 142, 142);
      color: rgb(0 0 0);
      
    }

    :global(.tab-panel) {
        font-size: 12px;
        font-family: Arial, sans-serif;
        color:white;
    }

  </style>
  
