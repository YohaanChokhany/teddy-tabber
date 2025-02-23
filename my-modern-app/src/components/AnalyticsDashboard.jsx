import React, { useMemo } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts'
import '../styles/Analytics.css'
const data = [
    { name: 'Entertainment', value: 8 },
    { name: 'Education', value: 7 },
    { name: 'Tech', value: 3 },
    { name: 'Health & Wellness', value: 6 },
    { name: 'Other', value: 7 }
]
const COLORS = ['#8B6F4E', '#B4A08F', '#DACBB7', '#EDE5DD', '#6E5C4A']
function AnalyticsDashboard() {
    const lineData = useMemo(() => {
        const arr = []
        for (let i = 6; i >= 0; i--) {
            const d = new Date()
            d.setDate(d.getDate() - i)
            const formatted = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            arr.push({ date: formatted, score: Math.floor(Math.random() * 4000) + 100 })
        }
        return arr
    }, [])
    return (
        <div className="analytics-container">
            <div className="charts">
                <div className="chart-card">
                    <h3>Data Analytics</h3>

                    <h4>Tab Categories</h4>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie data={data} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value">
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]}/>
                                ))}
                            </Pie>
                            <Tooltip/>
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="chart-card">
                    <h4>Your Weekly Scores</h4>
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

        </div>
    )
}
export default AnalyticsDashboard
