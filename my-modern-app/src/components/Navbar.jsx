import React, { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import '../styles/Navbar.css'

function Navbar() {
    const { isAuthenticated, user, logout, loginWithRedirect } = useAuth0()
    const [showDropdown, setShowDropdown] = useState(false)

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <h2>Bear Necessities</h2>
            </div>
            <div className="navbar-buttons">
                <button className="navbar-button" onClick={() => window.location.href = '/home'}>Home</button>
                <button className="navbar-button" onClick={() => window.location.href = '/your-tab-management-stats'}>Analytics Dashboard</button>
                <button className="navbar-button" onClick={() => window.location.href = '/about-us'}>About Us</button>

                {/* Account Dropdown Section */}
                <div className="account-dropdown">
                    <button className="navbar-button-account" onClick={() => setShowDropdown(!showDropdown)}>
                        Account
                    </button>
                    {showDropdown && (
                        <div className="dropdown-content">
                            {isAuthenticated ? (
                                <>
                                    <p><strong>Username:</strong> {user.nickname}</p>
                                    <p><strong>Email:</strong> {user.email}</p>
                                    <button className="logout-btn" onClick={() => logout({ returnTo: window.location.origin })}>
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <button className="login-btn" onClick={() => loginWithRedirect()}>
                                    Log in
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </nav>
    )
}

export default Navbar
