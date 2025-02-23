import React from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts'

const data = [
    { name: 'Apr 24', value: 400 },
    { name: 'May 22', value: 200 },
    { name: 'Jun 19', value: 300 },
    { name: 'Jul 17', value: 350 },
    { name: 'Aug 14', value: 100 }
]

const COLORS = ['#8B6F4E', '#B4A08F', '#DACBB7', '#EDE5DD', '#6E5C4A']

const lineData = [
    { date: 'Apr 24', score: 240 },
    { date: 'May 22', score: 400 },
    { date: 'Jun 19', score: 300 },
    { date: 'Jul 17', score: 450 },
    { date: 'Aug 14', score: 380 }
]

function AnalyticsDashboard() {
    return (
        <div className="analytics-container">
            <div className="charts">
                <div className="chart-card">
                    <h3>Tab Categories</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie data={data} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value">
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="chart-card">
                    <h3>Score over the week</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={lineData}>
                            <XAxis dataKey="date" />
                            <YAxis />
                            <CartesianGrid strokeDasharray="3 3" />
                            <Line type="monotone" dataKey="score" stroke="#8B6F4E" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
            <div className="score-section">
                <div className="score-card positive">
                    <span>↑</span>
                    <p>+2.34%</p>
                    <p>Week over week</p>
                </div>
                <div className="score-card negative">
                    <span>↓</span>
                    <p>-1.25%</p>
                    <p>Week over week</p>
                </div>
            </div>
        </div>
    )
}

export default AnalyticsDashboard
