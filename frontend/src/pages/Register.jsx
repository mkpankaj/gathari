import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useToast } from '../context/ToastContext'

export default function Register() {
  const [form, setForm] = useState({ user_id: '', user_name: '', password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const toast = useToast()

  const update = field => e => setForm(f => ({ ...f, [field]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    if (form.password !== form.confirm_password) {
      toast.show('Passwords do not match', 'error')
      return
    }
    setLoading(true)
    try {
      await api.post('/api/auth/register', form)
      toast.show('Account created — please sign in')
      navigate('/login')
    } catch (err) {
      toast.show(err.response?.data?.detail || 'Registration failed', 'error')
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
          <h2>Create account</h2>
          <p className="auth-subtitle">Join to track Nifty 50 stocks</p>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>User ID</label>
              <input value={form.user_id} onChange={update('user_id')} required autoFocus placeholder="choose a user id" />
            </div>
            <div className="form-group">
              <label>Name</label>
              <input value={form.user_name} onChange={update('user_name')} required placeholder="your name" />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={update('password')} required placeholder="••••••••" />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" value={form.confirm_password} onChange={update('confirm_password')} required placeholder="••••••••" />
            </div>
            <button className="btn btn-primary form-submit" disabled={loading}>
              {loading ? 'Creating…' : 'Create account'}
            </button>
          </form>
          <p className="form-footer">Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </div>
    </div>
  )
}
