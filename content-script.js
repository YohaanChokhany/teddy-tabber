
try {
    // Get current tab info
    const tabInfo = {
        title: document.title || '',
        url: window.location.href || document.location.href
    };

    // Only proceed if we have valid tab info
    if (tabInfo.url) {
        fetch('http://127.0.0.1:5000/categorize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tabInfo)
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    } else {
        console.error('Unable to get tab URL');
    }
} catch (error) {
    console.error('Content script error:', error);
}
