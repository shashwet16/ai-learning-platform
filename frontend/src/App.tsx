import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { ChatPage } from './pages/ChatPage'
import { CourseDetailPage } from './pages/CourseDetailPage'
import { CoursesPage } from './pages/CoursesPage'
import { DashboardPage } from './pages/DashboardPage'
import { LessonPage } from './pages/LessonPage'
import { LoginPage } from './pages/LoginPage'
import { PracticePage } from './pages/PracticePage'
import { QuizPage } from './pages/QuizPage'
import { RegisterPage } from './pages/RegisterPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
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
