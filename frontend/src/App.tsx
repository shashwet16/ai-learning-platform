import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ChatPage } from './pages/ChatPage'
import { CourseDetailPage } from './pages/CourseDetailPage'
import { CoursesPage } from './pages/CoursesPage'
import { LessonPage } from './pages/LessonPage'
import { LoginPage } from './pages/LoginPage'
import { PracticePage } from './pages/PracticePage'
import { QuizPage } from './pages/QuizPage'
import { RegisterPage } from './pages/RegisterPage'

function HomePage() {
  const { user } = useAuth()

  if (!user) {
    // ProtectedRoute guarantees this never happens; satisfies TypeScript's
    // null check and fails safe if it somehow did.
    return null
  }

  return (
    <div className="home-page">
      <span className="kicker">Dashboard</span>
      <h1>Welcome back.</h1>
      <p style={{ color: 'var(--ink-soft)', margin: '16px 0 32px' }}>
        You're signed in as {user.email}.
      </p>
      <div className="home-page__actions">
        <Link to="/courses" className="btn btn-primary">
          Browse courses
        </Link>
        <Link to="/chat" className="btn btn-quiet">
          Chat with your AI tutor
        </Link>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/courses" element={<CoursesPage />} />
              <Route path="/courses/:courseId" element={<CourseDetailPage />} />
              <Route path="/lessons/:lessonId" element={<LessonPage />} />
              <Route path="/lessons/:lessonId/quiz" element={<QuizPage />} />
              <Route path="/practice" element={<PracticePage />} />
              <Route path="/chat" element={<ChatPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
