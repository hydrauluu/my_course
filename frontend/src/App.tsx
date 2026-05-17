import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { Layout } from '@/components/layout'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { LecturesPage } from '@/pages/LecturesPage'
import { LectureDetailPage } from '@/pages/LectureDetailPage'
import { AssignmentDetailPage } from '@/pages/AssignmentDetailPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/lectures" element={<LecturesPage />} />
          <Route path="/lectures/:number" element={<LectureDetailPage />} />
          <Route path="/assignments/:id" element={<AssignmentDetailPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}
