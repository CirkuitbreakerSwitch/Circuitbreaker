import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

function Charts() {
  const [timelineData, setTimelineData] = useState([])
  const [toolData, setToolData] = useState([])

  useEffect(() => {
    // Demo data for now
    setTimelineData([
      { time: '00:00', blocked: 2, allowed: 1 },
      { time: '04:00', blocked: 1, allowed: 2 },
      { time: '08:00', blocked: 4, allowed: 1 },
      { time: '12:00', blocked: 3, allowed: 3 },
      { time: '16:00', blocked: 5, allowed: 2 },
      { time: '20:00', blocked: 4, allowed: 1 },
    ])

    setToolData([
      { name: 'file.delete', count: 15, blocked: 12 },
      { name: 'db.query', count: 8, blocked: 6 },
      { name: 'deploy.execute', count: 5, blocked: 0 },
      { name: 'file.read', count: 25, blocked: 0 },
    ])
  }, [])

  const riskData = [
    { name: 'Critical', value: 4, color: '#ff4444' },
    { name: 'High', value: 8, color: '#ff8800' },
    { name: 'Medium', value: 3, color: '#ffaa00' },
    { name: 'Low', value: 15, color: '#00cc00' },
  ]

  return (
    <div className="charts-section">
      <h2>Analytics</h2>
      
      <div className="charts-grid">
        {/* Timeline Chart */}
        <div className="chart-card">
          <h3>Blocks Over Time (24h)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Line type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="allowed" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Tools Chart */}
        <div className="chart-card">
          <h3>Top Tools by Usage</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={toolData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="count" fill="#60a5fa" />
              <Bar dataKey="blocked" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="chart-card">
          <h3>Risk Level Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="legend">
            {riskData.map((item) => (
              <span key={item.name} className="legend-item">
                <span className="dot" style={{ backgroundColor: item.color }}></span>
                {item.name}: {item.value}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Charts