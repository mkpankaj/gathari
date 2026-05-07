import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useToast } from '../context/ToastContext'

export default function Login() {
  const [form, setForm] = useState({ user_id: '', password: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const toast = useToast()

  const update = field => e => setForm(f => ({ ...f, [field]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/api/auth/login', form)
      localStorage.setItem('token', data.access_token)
      navigate('/dashboard')
    } catch (err) {
      toast.show(err.response?.data?.detail || 'Login failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-layout">
      <div className="auth-panel">
        <div className="auth-brand">
          <span className="auth-logo-mark">G</span>
          <h1 className="auth-title">Gathari</h1>
          <p className="auth-tagline">Nifty 50 &nbsp;·&nbsp; <em>Market Intelligence</em></p>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-form-wrap">
          <h2>Sign in</h2>
          <p className="auth-subtitle">Access your market dashboard</p>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>User ID</label>
              <input value={form.user_id} onChange={update('user_id')} required autoFocus placeholder="your user id" />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={update('password')} required placeholder="••••••••" />
            </div>
            <button className="btn btn-primary form-submit" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
          <p className="form-footer">No account? <Link to="/register">Register</Link></p>
        </div>
      </div>
    </div>
  )
}
