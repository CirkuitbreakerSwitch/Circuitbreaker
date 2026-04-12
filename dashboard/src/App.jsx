import { useState, useEffect } from 'react'
import './App.css'
import Charts from './components/Charts'

function App() {
  const [stats, setStats] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchEvents()
    const interval = setInterval(() => {
      fetchStats()
      fetchEvents()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      if (!response.ok) throw new Error('API not available')
      const data = await response.json()
      setStats(data)
      setError(null)
    } catch (error) {
      console.log('Stats API error:', error.message)
      setError('API not connected - showing demo data')
      setStats({
        total_evaluations: 6,
        blocked: 4,
        escalated: 0,
        allowed: 2,
        block_rate: 66.67,
        period: '24h'
      })
    }
  }

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/events?limit=10')
      if (!response.ok) throw new Error('API not available')
      const data = await response.json()
      setEvents(data)
      setLoading(false)
    } catch (error) {
      console.log('Events API error:', error.message)
      setEvents([
        {
          id: '1',
          tool: 'file.delete',
          action: 'block',
          risk_level: 'high',
          reason: "Policy 'No File Deletion in Production' matched",
          environment: 'production',
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          tool: 'db.query',
          action: 'block',
          risk_level: 'critical',
          reason: "Policy 'No DROP TABLE Statements' matched",
          environment: 'production',
          timestamp: new Date(Date.now() - 60000).toISOString()
        },
        {
          id: '3',
          tool: 'file.read',
          action: 'allow',
          risk_level: 'low',
          reason: 'No matching policy',
          environment: 'development',
          timestamp: new Date(Date.now() - 120000).toISOString()
        }
      ])
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

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

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

      <Charts />
    </div>
  )
}

export default App