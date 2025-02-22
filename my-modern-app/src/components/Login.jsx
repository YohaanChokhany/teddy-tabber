import '../styles/Login.css'
import { useAuth0 } from '@auth0/auth0-react'

function Login() {
    const { loginWithRedirect } = useAuth0()

    const handleGoogleLogin = () => {
        loginWithRedirect({
            connection: 'google-oauth2'
        })
    }

    const handleSignUp = () => {
        loginWithRedirect({
            screen_hint: 'signup',
        })
    }

    return (
        <div className="navbar">
            <button onClick={handleGoogleLogin} className="google-login-btn login-btn">
                Login with Google
            </button>
            <p className="signup-link">
                Don't have an account? <a href="#" onClick={handleSignUp}>Sign up</a>
            </p>
        </div>
    )
}

export default Login