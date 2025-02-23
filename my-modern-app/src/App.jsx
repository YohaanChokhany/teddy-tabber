import React, { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import Leaderboard from './components/Leaderboard';
import Login from './components/Login';
import Account from './components/Account';
import './App.css';
import './styles/Navbar.css';

function App() {
    const { isLoading, isAuthenticated, error } = useAuth0();

    useEffect(() => {
        const username = localStorage.getItem("username");

        if (!username) {
            const enteredUsername = prompt("Enter your username:");
            if (enteredUsername) {
                localStorage.setItem("username", enteredUsername);

                fetch("https://api.ipify.org")
                    .then(response => response.text())
                    .then(ipAddress => {
                        fetch("http://127.0.0.1:5000/api/store-user", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ username: enteredUsername, ip_address: ipAddress })
                        })
                            .then(response => response.json())
                            .then(data => console.log("User stored:", data))
                            .catch(error => console.error("Error storing user:", error));
                    });
            }
        }
    }, []);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Oops... {error.message}</div>;
    }

    return (
        <div>
            <div className="navbar">
                <div className="navbar-buttons">
                    <a className="navbar-button" href="#home">Home</a>
                    <a className="navbar-button" href="#analytics">Analytics Dashboard</a>
                    <a className="navbar-button" href="#about">About Us</a>
                    <a className="navbar-button" href="#leaderboard">Global Leaderboard</a>
                </div>
            </div>
            <div className="main-container">
                <div id="home" className="section">
                    <h1>Home</h1>
                    {isAuthenticated ? <Account /> : <Login />}
                </div>
                <div id="analytics" className="section">
                    <h1>Analytics Dashboard</h1>
                </div>
                <div id="about" className="section">
                    <h1>About Us</h1>
                    <p>We decided to make this app because...</p>
                </div>
                <div id="leaderboard" className="section">
                    <h1>Global Leaderboard</h1>
                    <Leaderboard />
                </div>
            </div>
        </div>
    );
}

export default App;