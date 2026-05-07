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

const TIMELINE_DAYS = { '1M': 30, '3M': 90, '6M': 180, '9M': 270, '1Y': 365, '1.5Y': 548, '2Y': 730 }

function timelineCutoff(timeline) {
  const days = TIMELINE_DAYS[timeline] ?? 730
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d
}

function fmtAxisDate(dateStr, timeline) {
  const d = new Date(dateStr)
  if (['1M', '3M', '6M'].includes(timeline))
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
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

const CHART_TOOLTIP = {
  contentStyle: {
    background: '#141720',
    border: '1px solid #2a3050',
    borderRadius: '3px',
    fontSize: '0.78rem',
    fontFamily: 'JetBrains Mono, monospace',
    color: '#dfe3f0',
    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
  },
  labelStyle: { color: '#4a5070', marginBottom: '2px' },
  cursor: { stroke: '#f0c040', strokeWidth: 1, strokeDasharray: '4 4' },
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
                <div className="stock-name">
                  {data.name}
                  <span className="stock-symbol">{symbol.replace('.NS', '')}</span>
                </div>
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
                <span className="stat-label">Slope / day</span>
                <span className="stat-value">
                  {data.slope_pct > 0 ? '+' : ''}{data.slope_pct.toFixed(4)}%
                </span>
              </div>
            </div>

            <TimelineTabs value={timeline} onChange={setTimeline} />

            <div className="card">
              <div className="card-body">
                {data.prices?.length > 0 ? (
                  <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.prices} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e2235" vertical={false} />
                        <XAxis
                          dataKey="trade_date"
                          tickFormatter={d => fmtAxisDate(d, timeline)}
                          tick={{ fontSize: 10, fill: '#4a5070', fontFamily: 'JetBrains Mono, monospace' }}
                          axisLine={{ stroke: '#1e2235' }}
                          tickLine={false}
                          minTickGap={52}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          tick={{ fontSize: 10, fill: '#4a5070', fontFamily: 'JetBrains Mono, monospace' }}
                          tickFormatter={v => `₹${Number(v).toLocaleString('en-IN')}`}
                          axisLine={false}
                          tickLine={false}
                          width={80}
                        />
                        <Tooltip
                          {...CHART_TOOLTIP}
                          formatter={v => [`₹${Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Close']}
                          labelFormatter={l => `Date: ${l}`}
                        />
                        <Line
                          type="monotone"
                          dataKey="close"
                          stroke="#f0c040"
                          dot={false}
                          strokeWidth={1.8}
                          activeDot={{ r: 4, fill: '#f0c040', stroke: '#07080d', strokeWidth: 2 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="empty">No price data for this timeline</div>
                )}
              </div>
            </div>

            {(() => {
              const cutoff = timelineCutoff(timeline)
              const filtered = (data.headlines ?? []).filter(h =>
                h.published_at ? new Date(h.published_at) >= cutoff : false
              )
              return filtered.length > 0 ? (
                <div className="card" style={{ marginTop: '1.25rem' }}>
                  <div className="card-body">
                    <div className="headlines-header">
                      <h3>News</h3>
                      <span className="timeline-pill">{timeline}</span>
                    </div>
                    {filtered.map((h, i) => (
                      <div key={i} className="headline-item">
                        <a href={h.url} target="_blank" rel="noreferrer">{h.headline}</a>
                        <div className="headline-source">
                          {[h.source, h.published_at ? fmtPubDate(h.published_at) : null].filter(Boolean).join(' · ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null
            })()}
          </>
        )}
      </div>
    </>
  )
}
