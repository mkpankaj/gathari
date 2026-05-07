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
  if (['1M', '3M', '6M'].includes(timeline)) return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
  return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
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
                        tickFormatter={v => Number(v).toLocaleString('en-IN')}
                        width={72}
                      />
                      <Tooltip
                        formatter={v => [Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 }), 'Close']}
                        labelFormatter={l => `Date: ${l}`}
                      />
                      <Line type="monotone" dataKey="close" stroke="#2563eb" dot={false} strokeWidth={2} />
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
