import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import Leaderboard from './components/Leaderboard';
import Login from './components/Login';
import Account from './components/Account';
import './App.css';
import './styles/Navbar.css';

function App() {
    const { isLoading, isAuthenticated, error } = useAuth0();

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Oops... {error.message}</div>;
    }

    return (
        <div className="main-container">
            <div className="navbar">
                <div className="navbar-brand">
                    <h2>My App</h2>
                </div>
                <div className="navbar-buttons">
                    <button className="navbar-button" onClick={() => window.location.href = '/home'}>Home</button>
                    <button className="navbar-button" onClick={() => window.location.href = '/your-tab-management-stats'}>Analytics Dashboard</button>
                </div>
            </div>
            <div className="header">
                {isAuthenticated ? (
                    <Account />
                ) : (
                    <Login />
                )}
            </div>
            <div className="leaderboard-section">
                <Leaderboard />
            </div>
        </div>
    );
}

export default App;