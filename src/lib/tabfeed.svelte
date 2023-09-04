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
      <Tab>Personal</Tab>
      <Tab>Social</Tab>
      <Tab>Global</Tab>
      <Tab>Trending</Tab>
    </TabList>
    <TabPanels>
      <TabPanel>Personal Content</TabPanel>
      <TabPanel>Social Content</TabPanel>
      <TabPanel>Global Content</TabPanel>
      <TabPanel>Trending Content</TabPanel>
    </TabPanels>
  </TabGroup>
  