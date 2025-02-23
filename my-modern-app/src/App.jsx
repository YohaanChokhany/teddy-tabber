import React, { useState, useRef } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import Leaderboard from './components/Leaderboard'
import Login from './components/Login'
import Account from './components/Account'
import AboutUs from './components/AboutUs'
import bearImage from './assets/bear_hi_wave_1.png';

/**/


import './App.css'
import './styles/Navbar.css'
import './styles/Leaderboard.css'
import './styles/AboutUs.css'
import './styles/Analytics.css'

import AnalyticsDashboard from './components/AnalyticsDashboard'


function App() {
    const { isLoading, isAuthenticated, error, user, logout } = useAuth0()
    const [showAccountPopup, setShowAccountPopup] = useState(false)
    const [showAnalytics, setShowAnalytics] = useState(false)
    const [ipAddress, setIpAddress] = useState('')
    const aboutUsRef = useRef(null)
    const analyticsRef = useRef(null)

    useEffect(() => {
        const fetchIpAddress = async () => {
            try {
                const response = await fetch('https://api.ipify.org?format=json')
                const data = await response.json()
                setIpAddress(data.ip)
            } catch (error) {
                console.error('Error fetching IP address:', error)
            }
        }

        fetchIpAddress()
    }, [])

    const scrollToAboutUs = () => {
        aboutUsRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const scrollToAnalytics = () => {
        setAnalyticsKey(prev => prev + 1)
        analyticsRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    if (isLoading) return (
        <div style={{ backgroundColor: '#f9f6f2', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <img src={bearImage} alt="Loading..." style={{ width: '5rem', height: 'auto' }} />
            <p style={{ marginTop: '10px', fontSize: '20px', color: '#c27f54' , fontWeight: "bold"}}>Loading...</p>
        </div>
    );
    if (error) return <div>Oops... {error.message}</div>

    return (
        <div className="main-container">
            <div className="navbar">
                <div className="navbar-brand">
                    <h2>Bear Necessities</h2>
                </div>
                <div className="navbar-buttons">
                    <button className="navbar-button" onClick={() => window.location.href = '/home'}>Home</button>
                    <button className="navbar-button" onClick={() => window.location.href = '/your-tab-management-stats'}>Analytics Dashboard</button>
                    <button className="navbar-button" onClick={scrollToAboutUs}>About Us</button>
                    <button className="navbar-button" onClick={scrollToAnalytics}>Data Analytics</button>
                </div>
                <button className="navbar-button-account" onClick={() => setShowAccountPopup(prev => !prev)}>Account</button>
            </div>
            <div className="header">
                {isAuthenticated ? <Account /> : <Login />}
            </div>
            <div className="leaderboard-section">
                <Leaderboard />
            </div>
            <div ref={aboutUsRef} className="about-us-section">
                <AboutUs />
            </div>
            <div ref={analyticsRef} className="analytics-section">
                <AnalyticsDashboard key={analyticsKey} />
            </div>
            {showAccountPopup && (
                <>

                    <div className="popup">
                        <div className="popup-inner">
                            {isAuthenticated && user ? (
                                <>
                                    <div className="account-text">
                                        <h2>Your Account</h2>
                                        <p>Username: {user.nickname}</p>
                                        <p>Email: {user.email}</p>
                                    </div>
                                    <button onClick={() => logout({ returnTo: window.location.origin })}>Logout</button>
                                </>
                            ) : (
                                <Login />
                            )}
                            <button className="close-btn" onClick={() => setShowAccountPopup(false)}>Close</button>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}

export default App
