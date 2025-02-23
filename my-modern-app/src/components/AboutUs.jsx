import React from 'react';
import '../styles/AboutUs.css';

const AboutUs = () => {
    return (
        <div className="about-us-container">
            <h2>About Us</h2>
            <p>
                We're three CS students who realized that having 100+ browser tabs open wasn't just
                crashing our browsers - it was killing our productivity. We decided to build Bear Necessities
                to incentivize tab management. Our mission is to provide a fun and engaging way to manage your
                tabs and improve productivity!
            </p>
            <h3>Features</h3>
            <ul>
                <li>Smart tab grouping by project and task to maintain focus</li>
                <li>Productivity scoring to track tab health over time</li>
                <li>Analytics to identify time-wasting tab habits</li>
                <li>Leaderboard to compete on who has the best tab management!</li>
            </ul>
        </div>
    );
};

export default AboutUs;
