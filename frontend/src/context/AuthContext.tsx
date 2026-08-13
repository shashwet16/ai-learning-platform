import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import {
  apiRequest,
  clearStoredToken,
  getStoredToken,
  setStoredToken,
} from '../api/client'

export interface User {
  id: string
  email: string
  full_name: string
  created_at: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = getStoredToken()
    if (!token) {
      setIsLoading(false)
      return
    }
    // A stored token could be stale (expired, or its user deleted server-
    // side) — /auth/me is the source of truth, not the mere presence of a
    // token in localStorage.
    apiRequest<User>('/auth/me')
      .then(setUser)
      .catch(() => clearStoredToken())
      .finally(() => setIsLoading(false))
  }, [])

  async function login(email: string, password: string): Promise<void> {
    const { access_token: accessToken } = await apiRequest<TokenResponse>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ email, password }) },
    )
    setStoredToken(accessToken)
    const me = await apiRequest<User>('/auth/me')
    setUser(me)
  }

  async function register(
    email: string,
    password: string,
    fullName: string,
  ): Promise<User> {
    return apiRequest<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
  }

  function logout(): void {
    clearStoredToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (ctx === null) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
