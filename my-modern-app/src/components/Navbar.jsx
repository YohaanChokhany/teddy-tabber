import '../styles/Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>Bear Necessities</h2>
      </div>
      <div className="auth-buttons">
        <button className="login-btn">Login</button>
        <button className="signup-btn">Sign Up</button>
      </div>
    </nav>
  )
}

export default Navbar 