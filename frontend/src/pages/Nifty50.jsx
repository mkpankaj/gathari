import { useEffect, useState } from 'react'
import {
  CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import api from '../api'
import Navbar from '../components/Navbar'
import TimelineTabs from '../components/TimelineTabs'
import { useToast } from '../context/ToastContext'

function fmtAxisDate(dateStr, timeline) {
  const d = new Date(dateStr)
  if (['1M', '3M', '6M'].includes(timeline))
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
  return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
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

export default function Nifty50() {
  const [timeline, setTimeline] = useState('2Y')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  useEffect(() => {
    setLoading(true)
    api.get(`/api/nifty50?timeline=${timeline}`)
      .then(r => setData(r.data))
      .catch(() => toast.show('Failed to load Nifty 50 data', 'error'))
      .finally(() => setLoading(false))
  }, [timeline])

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="page-header">
          <h1>Nifty 50</h1>
          <p className="subtitle">NSE Composite Index</p>
        </div>
        <TimelineTabs value={timeline} onChange={setTimeline} />
        {loading ? (
          <div className="loading">Loading…</div>
        ) : (
          <div className="card">
            <div className="card-body">
              {data?.prices?.length > 0 ? (
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
                        tickFormatter={v => Number(v).toLocaleString('en-IN')}
                        axisLine={false}
                        tickLine={false}
                        width={72}
                      />
                      <Tooltip
                        {...CHART_TOOLTIP}
                        formatter={v => [Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 }), 'Close']}
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
                <div className="empty">No data available. Run a refresh first.</div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  )
}
