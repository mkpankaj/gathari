import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import Navbar from '../components/Navbar'
import TimelineTabs from '../components/TimelineTabs'
import TrendBadge from '../components/TrendBadge'
import { useToast } from '../context/ToastContext'

function deltaClass(v) {
  if (v > 0) return 'delta-up'
  if (v < 0) return 'delta-down'
  return 'delta-neutral'
}

export default function Dashboard() {
  const [timeline, setTimeline] = useState('2Y')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const toast = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    api.get(`/api/dashboard?timeline=${timeline}`)
      .then(r => setData(r.data))
      .catch(() => toast.show('Failed to load dashboard', 'error'))
      .finally(() => setLoading(false))
  }, [timeline])

  async function handleRefresh() {
    setRefreshing(true)
    try {
      await api.post('/api/refresh')
      toast.show('Data refreshed')
      const r = await api.get(`/api/dashboard?timeline=${timeline}`)
      setData(r.data)
    } catch {
      toast.show('Refresh failed', 'error')
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="dashboard-toolbar">
          <button className="btn btn-outline btn-sm" onClick={() => navigate('/nifty50')}>
            Nifty 50
          </button>
          <button className="btn btn-primary btn-sm" onClick={handleRefresh} disabled={refreshing}>
            {refreshing ? 'Refreshing…' : 'Refresh Data'}
          </button>
        </div>

        <TimelineTabs value={timeline} onChange={setTimeline} />

        {loading ? (
          <div className="loading">Loading…</div>
        ) : (
          <div className="card">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Company</th>
                    <th>Industry</th>
                    <th>Trend</th>
                    <th className="text-right">Delta %</th>
                    <th className="text-right">Last Price</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.rows?.map(row => (
                    <tr key={row.symbol}>
                      <td>
                        <Link to={`/stocks/${row.symbol}`} className="text-mono">
                          {row.symbol.replace('.NS', '')}
                        </Link>
                      </td>
                      <td style={{ color: 'var(--text)', fontWeight: 500 }}>{row.name}</td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{row.industry || '—'}</td>
                      <td><TrendBadge trend={row.trend} /></td>
                      <td className={`text-right ${deltaClass(row.delta_pct)}`}>
                        {row.delta_pct > 0 ? '+' : ''}{row.delta_pct.toFixed(2)}%
                      </td>
                      <td className="text-right text-mono">
                        {row.last_price != null
                          ? `₹${row.last_price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
