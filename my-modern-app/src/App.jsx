import React from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import Leaderboard from './components/Leaderboard'
import Login from './components/Login'
import './App.css'

function App() {
    const { isLoading, isAuthenticated, error, logout } = useAuth0()

    if (isLoading) {
        return <div>Loading...</div>
    }

    if (error) {
        return <div>Oops... {error.message}</div>
    }

    return (
        <div className="main-container">
            <div className="header">
                {isAuthenticated ? (
                    <button onClick={() => logout({ returnTo: window.location.origin })}>
                        Your Account
                    </button>
                ) : (
                    <Login />
                )}
            </div>
            <div className="leaderboard-section">
                <Leaderboard />
            </div>
        </div>
    )
}

export default App