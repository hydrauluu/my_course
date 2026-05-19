import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { ToastProvider } from '@/hooks/useToast'
import { Layout } from '@/components/layout'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { LecturesPage } from '@/pages/LecturesPage'
import { LectureDetailPage } from '@/pages/LectureDetailPage'
import { AssignmentDetailPage } from '@/pages/AssignmentDetailPage'

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <ErrorBoundary>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/lectures" element={<ProtectedRoute><LecturesPage /></ProtectedRoute>} />
              <Route path="/lectures/:number" element={<ProtectedRoute><LectureDetailPage /></ProtectedRoute>} />
              <Route path="/assignments/:id" element={<ProtectedRoute><AssignmentDetailPage /></ProtectedRoute>} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </ErrorBoundary>
      </ToastProvider>
    </AuthProvider>
  )
}
