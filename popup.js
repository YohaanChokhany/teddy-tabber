const API_KEY = "2JYy39h8h79EgyLnvPL6bZjdAzTME";
const API_URL = "https://website-categorization.whoisxmlapi.com/api/v2";

async function getWebsiteCategory(url) {
  try {
    const domain = new URL(url).hostname;
    const response = await fetch(
            `${API_URL}?apiKey=${API_KEY}&domain=${encodeURIComponent(domain)}`,
            { method: "GET" }
    );

    if (!response.ok) {
      return "Uncategorized";
    }

    const data = await response.json();
    if (!data.categories || data.categories.length === 0) {
      return "Uncategorized";
    }

    return data.categories[0];
  } catch (error) {
    return "Uncategorized";
  }
}

document.getElementById('fetch-tabs').addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: "fetchTabs" }, (tabs) => {
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError.message);
      return;
    }

    const tabsWithTimes = tabs.map(tab => ({
      title: tab.title,
      url: tab.url,
      openTime: Date.now() - tab.lastAccessed
    }));

    tabsWithTimes.sort((a, b) => b.openTime - a.openTime);
    const topTabs = tabsWithTimes.slice(0, 3);

    const display = document.getElementById('tabs-display');
    display.innerHTML = topTabs.map(tab => `
          <div>
              <p><strong>Title:</strong> ${tab.title}</p>
              <p><strong>URL:</strong> ${tab.url}</p>
              <p><strong>Open for:</strong> ${Math.floor(tab.openTime / 1000)} seconds</p>
          </div>
      `).join('');
  });
});


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

async function groupTabsByCategory() {
  const tabs = await chrome.tabs.query({});
  const groupedTabs = {};

  for (const tab of tabs) {
    if (!tab.url) continue;

    const category = await getWebsiteCategory(tab.url);

    if (!groupedTabs[category]) {
      groupedTabs[category] = [];
    }
    groupedTabs[category].push(tab.id);
  }

  for (const [category, tabIds] of Object.entries(groupedTabs)) {
    if (tabIds.length) {
      try {
        const group = await chrome.tabs.group({ tabIds });
        await chrome.tabGroups.update(group, { title: category });
      } catch (err) {
        console.error(`Error grouping "${category}":`, err);
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", categorizeTabs);

const button = document.querySelector("button");
button.addEventListener("click", groupTabsByCategory);

document.addEventListener('DOMContentLoaded', () => {
  const checkboxes = document.querySelectorAll('.checkbox');

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('click', () => {
      checkbox.classList.toggle('checked');
    });
  });

  // Add button for running Python script
  const runPythonButton = document.createElement('button');
  runPythonButton.textContent = 'Run Python Script';
  runPythonButton.addEventListener('click', async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/run-python', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input_string: 'Your string here'  // Replace with your desired string
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to run Python script');
      }
      
      const result = await response.json();
      console.log('Python script output:', result);
    } catch (error) {
      console.error('Error running Python script:', error);
    }
  });
  
  document.body.appendChild(runPythonButton);
});

function checkAll() {
  document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => cb.checked = true);
}
function uncheckAll() {
  document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => cb.checked = false);
}
