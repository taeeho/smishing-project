import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ResultPage from './pages/ResultPage'
import CoachingPage from './pages/CoachingPage'
import KakaoCallback from './pages/KakaoCallback'
import LoginPage from './pages/LoginPage'
import ProfilePage from './pages/ProfilePage'
import TrendPage from './pages/TrendPage'
import HistoryPage from './pages/HistoryPage'

function App() {
  const isAuthed = !!localStorage.getItem('access_token')
  return (
    <Routes>
      <Route path="/login" element={isAuthed ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route path="/auth/kakao/callback" element={<KakaoCallback />} />
      <Route element={isAuthed ? <Layout /> : <Navigate to="/login" replace />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="/trend" element={<TrendPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/coaching" element={<CoachingPage />} />
      </Route>
    </Routes>
  )
}

export default App
