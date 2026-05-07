import { NavLink, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  function logout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <span className="navbar-brand">Gathari</span>
      <div className="navbar-links">
        <NavLink to="/dashboard">Markets</NavLink>
        <NavLink to="/nifty50">Index</NavLink>
      </div>
      <div className="navbar-actions">
        <button className="btn btn-outline btn-sm" onClick={logout}>Logout</button>
      </div>
    </nav>
  )
}
