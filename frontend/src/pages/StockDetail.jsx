import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import api from '../api'
import Navbar from '../components/Navbar'
import TimelineTabs from '../components/TimelineTabs'
import TrendBadge from '../components/TrendBadge'
import { useToast } from '../context/ToastContext'

function fmtAxisDate(dateStr, timeline) {
  const d = new Date(dateStr)
  if (timeline === '1M') return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
  if (['3M', '6M'].includes(timeline)) return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
  return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
}

function fmtPubDate(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

function deltaClass(v) {
  if (v > 0) return 'delta-up'
  if (v < 0) return 'delta-down'
  return 'delta-neutral'
}

export default function StockDetail() {
  const { symbol } = useParams()
  const [timeline, setTimeline] = useState('2Y')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  useEffect(() => {
    setLoading(true)
    api.get(`/api/stocks/${symbol}?timeline=${timeline}`)
      .then(r => setData(r.data))
      .catch(() => toast.show('Failed to load stock data', 'error'))
      .finally(() => setLoading(false))
  }, [symbol, timeline])

  return (
    <>
      <Navbar />
      <div className="container">
        {loading ? (
          <div className="loading">Loading…</div>
        ) : data && (
          <>
            <div className="stock-header">
              <div>
                <h1>
                  {data.name}{' '}
                  <span className="text-mono" style={{ fontWeight: 400, fontSize: '0.95rem', color: 'var(--text-muted)' }}>
                    {symbol.replace('.NS', '')}
                  </span>
                </h1>
                {data.industry && <div className="stock-meta">{data.industry}</div>}
              </div>
              <TrendBadge trend={data.trend} />
            </div>

            <div className="stock-stats">
              <div className="stat">
                <span className="stat-label">Last Price</span>
                <span className="stat-value">
                  {data.last_price != null
                    ? `₹${data.last_price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : '—'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Delta ({timeline})</span>
                <span className={`stat-value ${deltaClass(data.delta_pct)}`}>
                  {data.delta_pct > 0 ? '+' : ''}{data.delta_pct.toFixed(2)}%
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Slope</span>
                <span className="stat-value">
                  {data.slope_pct > 0 ? '+' : ''}{data.slope_pct.toFixed(4)}%/day
                </span>
              </div>
            </div>

            <TimelineTabs value={timeline} onChange={setTimeline} />

            <div className="card">
              <div className="card-body">
                {data.prices?.length > 0 ? (
                  <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.prices} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                          dataKey="trade_date"
                          tickFormatter={d => fmtAxisDate(d, timeline)}
                          tick={{ fontSize: 11 }}
                          minTickGap={48}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          tick={{ fontSize: 11 }}
                          tickFormatter={v => `₹${Number(v).toLocaleString('en-IN')}`}
                          width={80}
                        />
                        <Tooltip
                          formatter={v => [`₹${Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Close']}
                          labelFormatter={l => `Date: ${l}`}
                        />
                        <Line type="monotone" dataKey="close" stroke="#2563eb" dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="empty">No price data for this timeline</div>
                )}
              </div>
            </div>

            {data.headlines?.length > 0 && (
              <div className="card" style={{ marginTop: '1.25rem' }}>
                <div className="card-body">
                  <div className="headlines">
                    <h3>Recent News</h3>
                    {data.headlines.map((h, i) => (
                      <div key={i} className="headline-item">
                        <a href={h.url} target="_blank" rel="noreferrer">{h.headline}</a>
                        <div className="headline-source">
                          {[h.source, h.published_at ? fmtPubDate(h.published_at) : null].filter(Boolean).join(' · ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  )
}
