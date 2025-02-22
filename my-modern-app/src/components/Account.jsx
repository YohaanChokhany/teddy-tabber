import React from 'react'
import { useAuth0 } from '@auth0/auth0-react'

function Account() {
    const { user, logout } = useAuth0()
    const loginDate = new Date(user.updated_at)
    const currentDate = new Date()
    const daysSinceLogin = Math.floor((currentDate - loginDate) / (1000 * 60 * 60 * 24))

    const handleLogout = () => {
        logout({ returnTo: window.location.origin })
    }

    return (
        <div className="account-details">
            <h2>Your Account</h2>
            <p>Name: {user.name}</p>
            <p>Username: {user.nickname}</p>
            <p>Days since last login: {daysSinceLogin}</p>
            <button onClick={handleLogout} className="logout-btn">
                Logout
            </button>
        </div>
    )
}

export default Account