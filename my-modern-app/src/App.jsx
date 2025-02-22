import Leaderboard from './components/Leaderboard'
import Login from './components/Login'
import './App.css'

function App() {
  return (
    <div className="main-container">
      <div className="leaderboard-section">
        <Leaderboard />
      </div>
      <div className="login-section">
        <Login />
      </div>
    </div>
  )
}

export default App
