import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function SiteHeader() {
  const { user, logout } = useAuth()

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link to="/" className="site-header__wordmark">
          AI <em>Engineering</em>
        </Link>
        <nav className="site-header__nav">
          <Link to="/courses">Courses</Link>
          <Link to="/practice">Practice</Link>
          <Link to="/chat">Chat</Link>
          {user && <span className="site-header__user">{user.email}</span>}
          <button type="button" className="btn btn-quiet" onClick={logout}>
            Log out
          </button>
        </nav>
      </div>
    </header>
  )
}
