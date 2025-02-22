chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "categorizeTabs") {
        categorizeTabs();
        sendResponse({ status: "Tabs categorized" });
    }
});

async function categorizeTabs() {
    const tabs = await chrome.tabs.query({});
    console.log("Categorizing tabs:", tabs);
}
