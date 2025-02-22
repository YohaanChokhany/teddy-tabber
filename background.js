chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "fetchTabs") {
        chrome.tabs.query({}, (tabs) => {
            sendResponse(tabs);
        });
        return true; // Keep the message channel open for sendResponse
    }
});
