const express = require('express');
const mongoose = require('mongoose');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors()); // Allow requests from Chrome extension

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/TabTracker', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

const TabSchema = new mongoose.Schema({
    url: String,
    category: String,
    score: Number,
    timestamp: { type: Date, default: Date.now }
});

const UserSchema = new mongoose.Schema({
    _id: String,  // user_id
    total_score: { type: Number, default: 0 }
});

const Tab = mongoose.model('Tab', TabSchema);
const User = mongoose.model('User', UserSchema);

// WHOIS XML API Key
const API_KEY = "YOUR_WHOISXML_API_KEY";
const API_URL = "https://website-categorization.whoisxmlapi.com/api/v2";

// Scoring System
const CATEGORY_SCORES = {
    "Education": 5,
    "Productivity": 5,
    "Technology & Development": 2,
    "Finance & Investments": 2,
    "Health & Wellness": 2,
    "Social Media": -5,
    "Entertainment": -5,
    "Gaming": -5
};

// Home Route
app.get('/', (req, res) => {
    res.send("Welcome to Teddy Tabber! The API is running.");
});

// Process Tabs Route
app.post('/process-tabs', async (req, res) => {
    try {
        const { urls, user_id = "default_user" } = req.body;
        let total_score = 0;
        let tabEntries = [];

        for (const url of urls) {
            // Get category from API
            const response = await axios.get(API_URL, {
                params: { apiKey: API_KEY, url: url }
            });

            const category = response.data.categories?.[0] || "Unknown";
            let score = CATEGORY_SCORES[category] || 0;

            // Check if tab has been open for 2+ days
            const existingTab = await Tab.findOne({ url });
            if (existingTab) {
                const days_open = (new Date() - existingTab.timestamp) / (1000 * 60 * 60 * 24);
                if (days_open >= 2) {
                    score -= 2; // Deduct points for being open too long
                }
            }

            // Store in DB
            const tabEntry = await Tab.findOneAndUpdate(
                { url },
                { category, score, timestamp: new Date() },
                { upsert: true, new: true }
            );

            tabEntries.push(tabEntry);
            total_score += score;
        }

        // Update user score
        await User.findByIdAndUpdate(user_id, { $inc: { total_score } }, { upsert: true, new: true });

        res.json({ status: "success", tabs: tabEntries, total_score });
    } catch (error) {
        console.error("Error processing tabs:", error);
        res.status(500).json({ status: "error", message: "Internal Server Error" });
    }
});

// Start Server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
