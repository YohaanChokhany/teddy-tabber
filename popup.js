const tabsList = document.getElementById('tabs-list');
// Add the blur overlay div if it doesn't exist
let blurOverlay = tabsList.querySelector('.blur-overlay');
if (!blurOverlay) {
  blurOverlay = document.createElement('div');
  blurOverlay.className = 'blur-overlay';
  tabsList.parentElement.appendChild(blurOverlay);
}

// Add the top blur overlay div if it doesn't exist
let topBlurOverlay = tabsList.querySelector('.blur-overlay-top');
if (!topBlurOverlay) {
  topBlurOverlay = document.createElement('div');
  topBlurOverlay.className = 'blur-overlay-top';
  tabsList.parentElement.appendChild(topBlurOverlay);
}

// Update scroll listener to show/hide blur effect
const updateBlurVisibility = () => {
  const isScrollable = tabsList.scrollHeight > tabsList.clientHeight;
  const isScrolledToBottom = tabsList.scrollHeight - tabsList.scrollTop === tabsList.clientHeight;
  const isScrolledToTop = tabsList.scrollTop === 0;

  blurOverlay.style.opacity = isScrollable && !isScrolledToBottom ? '1' : '0';
  topBlurOverlay.style.opacity = isScrollable && !isScrolledToTop ? '1' : '0';
};

tabsList.addEventListener('scroll', updateBlurVisibility);

let tabs = [];

async function fetchAndCategorizeTabs() {
  try {
    // Get all tabs from all windows
    tabs = await chrome.tabs.query({});

    // Format tabs data for the API
    const tabsData = tabs.map(tab => ({
      id: tab.id,
      url: tab.url,
      title: tab.title
    }));

    // Call the categorize-batch endpoint
    const response = await fetch('http://127.0.0.1:5000/categorize-batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tabs: tabsData })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Process the categorized tabs
    const tabsList = document.getElementById('tabs-list');
    const template = document.getElementById('tabs-list-template');

    // Add console logs for debugging
    console.log('TabsList element:', tabsList);
    console.log('Template element:', template);
    console.log('API response:', data);

    if (!tabsList || !template) {
      throw new Error('Required DOM elements not found');
    }

    // Clear existing tabs
    tabsList.innerHTML = '';
    tabs = data.results;
    // Add categorized tabs to the list
    let tabPoints = 0;
    data.results.forEach(result => {
      const tabElement = template.content.cloneNode(true);
      const tabItem = tabElement.querySelector('.tab-item');

      if (!tabItem) {
        console.error('Tab item not found in template');
        return;
      }

      // Set the title
      const titleElement = tabItem.querySelector('.tab-title');
      if (titleElement) {
        titleElement.textContent = result.title;
        titleElement.title = result.url; // Show full URL on hover
      }

      // Set the icon based on category
      const iconElement = tabItem.querySelector('.tab-icon');
      if (iconElement) {
        const categoryEmoji = getCategoryEmoji(result.category);
        iconElement.textContent = categoryEmoji;
      }

      tabPoints += getCategoryPoints(result.category);
      
      tabsList.appendChild(tabElement);
    });
    updateBlurVisibility(); // Initial check

    // Update the tabs count in stats
    const tabsCountElement = document.getElementById('tabs-open');
    if (tabsCountElement) {
      tabsCountElement.textContent = tabs.length;
    }
    const tabPointsElement = document.getElementById("tab-points");
    if (tabPointsElement) {
      tabPointsElement.textContent = tabPoints;
    }
    document.getElementById('content').style.opacity = '1';
  } catch (error) {
    console.error('Error in fetchAndCategorizeTabs:', error);
  }
}

function getCategoryPoints(category) {
  const pointsMap = {
    'education': 500,
    'entertainment': -500,
    'productivity': 500,
    'tech_and_dev': 200,
    'finance': 200,
    'health_and_wellness': 200,
    'social_media': -500,
    'shopping': -200,
    'gaming': -500,
    'other': -100
  };
  return pointsMap[category] || 0;
}

function getCategoryEmoji(category) {
  const emojiMap = {
    'education': '📚',
    'entertainment': '🎬',
    'productivity': '💼',
    'tech_and_dev': '💻',
    'finance': '💰',
    'health_and_wellness': '🏥',
    'social_media': '📱',
    'shopping': '🛍️',
    'gaming': '🎮',
    'other': '🔴'
  };
  return emojiMap[category] || '🔴';
}

function getCategoryName(category) {
  const emojiMap = {
    'education': 'Education',
    'entertainment': 'Entertainment',
    'productivity': 'Productivity',
    'tech_and_dev': 'Tech & Dev',
    'finance': 'Finance',
    'health_and_wellness': 'Health & Wellness',
    'social_media': 'Social Media',
    'shopping': 'Shopping',
    'gaming': 'Gaming',
  };
  return emojiMap[category] || '';
}

// Add click handler to the fetch-tabs button
document.getElementById('group-tabs').addEventListener('click', groupTabsByCategory);

async function groupTabsByCategory() {
  const groupedTabs = {};

  for (const tab of tabs) {
    if (!tab.url) continue;

    const category = tab.category;

    if (!groupedTabs[category]) {
      groupedTabs[category] = [];
    }
    groupedTabs[category].push(tab.id);
  }

  console.log(groupedTabs);

  for (const [category, tabIds] of Object.entries(groupedTabs)) {
    if (category == "other") continue;
    if (tabIds.length) {
      try {
        const group = await chrome.tabs.group({ tabIds });
        await chrome.tabGroups.update(group, { title: getCategoryName(category) });
      } catch (err) {
        console.error(`Error grouping "${category}":`, err);
      }
    }
  }
}


// Fetch tabs when popup opens
document.addEventListener('DOMContentLoaded', fetchAndCategorizeTabs);

async function categorizeTabs() {
  const tabs = await chrome.tabs.query({});
  const categorizedTabs = await Promise.all(
      tabs.map(async (tab) => {
        if (!tab.url) {
          return { ...tab, category: "Uncategorized" };
        }

        const category = await getWebsiteCategory(tab.url);
        return { ...tab, category };
      })
  );

  const collator = new Intl.Collator();
  categorizedTabs.sort((a, b) => collator.compare(a.title, b.title));

  const groupedTabs = {};
  categorizedTabs.forEach((tab) => {
    if (!groupedTabs[tab.category]) {
      groupedTabs[tab.category] = [];
    }
    groupedTabs[tab.category].push(tab);
  });

  updatePopupUI(groupedTabs);
}

function updatePopupUI(groupedTabs) {
  const ul = document.querySelector("ul");
  ul.innerHTML = "";

  Object.entries(groupedTabs).forEach(([category, tabs]) => {
    const categoryHeader = document.createElement("h3");
    categoryHeader.textContent = category;
    ul.appendChild(categoryHeader);

    const template = document.getElementById("li_template");

    for (const tab of tabs) {
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

document.addEventListener("DOMContentLoaded", fetchAndCategorizeTabs);

const button = document.querySelector("button");
button.addEventListener("click", groupTabsByCategory);

document.addEventListener('DOMContentLoaded', () => {
  const checkboxes = document.querySelectorAll('.checkbox');

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('click', () => {
      checkbox.classList.toggle('checked');
    });
  });
});

function checkAll() {
  document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => cb.checked = true);
}
function uncheckAll() {
  document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => cb.checked = false);
}
