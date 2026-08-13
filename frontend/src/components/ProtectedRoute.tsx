import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute() {
  const { user, isLoading } = useAuth()

  // Don't decide anything while the mount-time /auth/me check (see M2.7)
  // is still in flight — on a fresh page load with a valid stored token,
  // `user` starts out null for a moment before that check resolves.
  // Redirecting during that window would incorrectly bounce an actually
  // logged-in user to /login before their session ever got a chance to
  // be verified.
  if (isLoading) {
    return <p className="loading-screen">Loading…</p>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
