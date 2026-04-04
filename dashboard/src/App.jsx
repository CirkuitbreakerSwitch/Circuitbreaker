import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [stats, setStats] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    fetchEvents()
    const interval = setInterval(fetchEvents, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/events?limit=10')
      const data = await response.json()
      setEvents(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching events:', error)
      setLoading(false)
    }
  }

  const getActionIcon = (action) => {
    switch (action) {
      case 'block': return '🚫'
      case 'escalate': return '⏸️'
      case 'allow': return '✅'
      default: return '❓'
    }
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'critical': return '#ff4444'
      case 'high': return '#ff8800'
      case 'medium': return '#ffaa00'
      case 'low': return '#00cc00'
      default: return '#888'
    }
  }

  if (loading) {
    return <div className="loading">Loading CircuitBreaker Dashboard...</div>
  }

  return (
    <div className="dashboard">
      <header>
        <h1>🛡️ CircuitBreaker Dashboard</h1>
        <p>Real-time AI Agent Protection</p>
      </header>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card total">
            <h3>Total Evaluations</h3>
            <div className="stat-value">{stats.total_evaluations}</div>
          </div>
          <div className="stat-card blocked">
            <h3>Blocked</h3>
            <div className="stat-value">{stats.blocked}</div>
            <div className="stat-percent">{stats.block_rate}%</div>
          </div>
          <div className="stat-card escalated">
            <h3>Escalated</h3>
            <div className="stat-value">{stats.escalated}</div>
          </div>
          <div className="stat-card allowed">
            <h3>Allowed</h3>
            <div className="stat-value">{stats.allowed}</div>
          </div>
        </div>
      )}

      <div className="events-section">
        <h2>Recent Events</h2>
        <div className="events-list">
          {events.length === 0 ? (
            <p className="no-events">No events yet. Run some tests!</p>
          ) : (
            events.map((event) => (
              <div key={event.id} className="event-card">
                <div className="event-header">
                  <span className="action-icon">{getActionIcon(event.action)}</span>
                  <span className="tool-name">{event.tool}</span>
                  <span 
                    className="risk-badge"
                    style={{ backgroundColor: getRiskColor(event.risk_level) }}
                  >
                    {event.risk_level}
                  </span>
                </div>
                <div className="event-details">
                  <p><strong>Action:</strong> {event.action}</p>
                  <p><strong>Reason:</strong> {event.reason || 'No reason provided'}</p>
                  <p><strong>Environment:</strong> {event.environment || 'unknown'}</p>
                  <p className="timestamp">
                    {new Date(event.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default App
