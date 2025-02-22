const API_KEY = "2JYy39h8h79EgyLnvPL6bZjdAzTME"; // Replace with your actual API key
const API_URL = "https://website-categorization.whoisxmlapi.com/api/v2";

// Function to fetch website category
async function getWebsiteCategory(url) {
  try {
    const domain = new URL(url).hostname;
    console.log(`Fetching category for: ${domain}`);

    const response = await fetch(
        `${API_URL}?apiKey=${API_KEY}&domain=${encodeURIComponent(domain)}`,
        { method: "GET" }
    );

    if (!response.ok) {
      console.error(`API Error: ${response.status} ${response.statusText}`);
      return "Uncategorized";
    }

    const data = await response.json();
    console.log(`Raw API response for ${domain}:`, data);

    // Check if categories exist
    if (!data.categories || data.categories.length === 0) {
      console.warn(`No categories found for ${domain}, defaulting to Uncategorized.`);
      return "Uncategorized";
    }

    console.log(`Category for ${domain}: ${data.categories[0]}`);
    return data.categories[0]; // Default to first category
  } catch (error) {
    console.error(`Error fetching website category for ${url}:`, error);
    return "Uncategorized";
  }
}

// Function to categorize open tabs
async function categorizeTabs() {
  console.log("Categorizing tabs...");

  const tabs = await chrome.tabs.query({});
  console.log(`Total tabs found: ${tabs.length}`);

  const categorizedTabs = await Promise.all(
      tabs.map(async (tab) => {
        if (!tab.url) {
          console.warn(`Skipping tab with no URL: ${tab.title}`);
          return { ...tab, category: "Uncategorized" };
        }

        console.log(`Processing tab: ${tab.title}, URL: ${tab.url}`);
        const category = await getWebsiteCategory(tab.url);
        console.log(`Categorized tab "${tab.title}" as "${category}"`);
        return { ...tab, category };
      })
  );

  // Sort tabs alphabetically within categories
  const collator = new Intl.Collator();
  categorizedTabs.sort((a, b) => collator.compare(a.title, b.title));

  // Group tabs by category
  const groupedTabs = {};
  categorizedTabs.forEach((tab) => {
    if (!groupedTabs[tab.category]) {
      groupedTabs[tab.category] = [];
    }
    groupedTabs[tab.category].push(tab);
  });

  console.log("Final grouped tabs:", groupedTabs);

  // Update UI with categorized tabs
  updatePopupUI(groupedTabs);
}

// Function to update popup UI
function updatePopupUI(groupedTabs) {
  console.log("Updating popup UI...");

  const ul = document.querySelector("ul");
  ul.innerHTML = ""; // Clear previous elements

  Object.entries(groupedTabs).forEach(([category, tabs]) => {
    console.log(`Adding category to UI: ${category}`);

    const categoryHeader = document.createElement("h3");
    categoryHeader.textContent = category;
    ul.appendChild(categoryHeader);

    const template = document.getElementById("li_template");

    for (const tab of tabs) {
      console.log(`Adding tab to UI: ${tab.title} under "${category}"`);

      const element = template.content.firstElementChild.cloneNode(true);
      element.querySelector(".title").textContent = tab.title;
      element.querySelector(".pathname").textContent = new URL(tab.url).pathname;
      element.querySelector("a").addEventListener("click", async () => {
        await chrome.tabs.update(tab.id, { active: true });
        await chrome.windows.update(tab.windowId, { focused: true });
      });

      ul.appendChild(element);
    }
  });
}

// Function to group tabs in Chrome by category
async function groupTabsByCategory() {
  console.log("Grouping tabs in Chrome...");

  const tabs = await chrome.tabs.query({});
  const groupedTabs = {};

  // Fetch categories for each tab
  for (const tab of tabs) {
    if (!tab.url) continue;

    console.log(`Fetching category for grouping: ${tab.title}`);
    const category = await getWebsiteCategory(tab.url);

    if (!groupedTabs[category]) {
      groupedTabs[category] = [];
    }
    groupedTabs[category].push(tab.id);
  }

  console.log("Tabs grouped by category:", groupedTabs);

  // Group tabs in Chrome
  for (const [category, tabIds] of Object.entries(groupedTabs)) {
    if (tabIds.length) {
      try {
        console.log(`Creating Chrome tab group: "${category}" with ${tabIds.length} tabs.`);
        const group = await chrome.tabs.group({ tabIds });
        await chrome.tabGroups.update(group, { title: category });
      } catch (err) {
        console.error(`Error grouping "${category}":`, err);
      }
    }
  }
}

// Initialize categorization when popup is loaded
document.addEventListener("DOMContentLoaded", categorizeTabs);

// Attach event listener to button for tab grouping
const button = document.querySelector("button");
button.addEventListener("click", groupTabsByCategory);