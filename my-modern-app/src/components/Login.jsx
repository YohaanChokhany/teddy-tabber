import '../styles/Login.css'
import { useAuth0 } from '@auth0/auth0-react'
import { Link } from 'react-router-dom'

function Login() {
    const { loginWithRedirect, isAuthenticated, logout } = useAuth0()

    const handleLogin = () => {
        loginWithRedirect()
    }

    const handleLogout = () => {
        logout({ returnTo: window.location.origin })
    }

    return (
        <div className="navbar">
            {isAuthenticated ? (
                <>
                    <Link to="/account" className="account-btn">
                        Your Account
                    </Link>
                    <button onClick={handleLogout} className="logout-btn">
                        Logout
                    </button>
                </>
            ) : (
                <>
                    <button onClick={handleLogin} className="login-btn">
                        Log in to continue
                    </button>
                </>
            )}
        </div>
    )
}

export default Login