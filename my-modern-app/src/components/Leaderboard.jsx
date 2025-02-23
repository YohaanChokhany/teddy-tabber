import '../styles/Leaderboard.css'

function Leaderboard() {
  // Dummy data - replace with actual data from your backend
  const leaderboardData = [
    { rank: 1, username: "BearMaster", score: 2500 },
    { rank: 2, username: "HoneyHunter", score: 2300 },
    { rank: 3, username: "WildExplorer", score: 2100 },
    { rank: 4, username: "ForestGuide", score: 1900 },
    { rank: 5, username: "NatureWalker", score: 1800 },
    { rank: 6, username: "BerryPicker", score: 1750 },
    { rank: 7, username: "MountainClimber", score: 1700 },
    { rank: 8, username: "RiverRafter", score: 1650 },
    { rank: 9, username: "TrailBlazer", score: 1600 },
    { rank: 10, username: "CampMaster", score: 1550 },
  ]

  const podiumOrder = [2, 1, 3] // Order for left, center, right positions

  return (
    <div className="leaderboard">
      <h1>Global Leaderboard</h1>
      
      <div className="podium-container">
        {podiumOrder.map(position => {
          const player = leaderboardData[position - 1]
          return (
            <div key={player.rank} className={`podium-position rank-${player.rank}`}>
              <div className="podium-player">
                <div className="player-name">{player.username}</div>
                <div className="player-score">{player.score}</div>
              </div>
              <div className="podium-platform">#{player.rank}</div>
            </div>
          )
        })}
      </div>

      <div className="other-ranks">
        {leaderboardData.slice(3).map((player) => (
          <div key={player.rank} className="rank-row">
            <span className="rank">#{player.rank}</span>
            <span className="username">{player.username}</span>
            <span className="score">{player.score}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Leaderboard 