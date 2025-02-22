import Navbar from './components/Navbar'
import Leaderboard from './components/Leaderboard'
import './App.css'

function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Leaderboard />
      </main>
    </div>
  )
}

export default App
