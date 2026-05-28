import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { ToastProvider } from '@/hooks/useToast'
import { Layout } from '@/components/layout'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { ErrorBoundary } from '@/components/ErrorBoundary'

const LoginPage = lazy(() => import('@/pages/LoginPage').then(m => ({ default: m.LoginPage })))
const DashboardPage = lazy(() => import('@/pages/DashboardPage').then(m => ({ default: m.DashboardPage })))
const LecturesPage = lazy(() => import('@/pages/LecturesPage').then(m => ({ default: m.LecturesPage })))
const LectureDetailPage = lazy(() => import('@/pages/LectureDetailPage').then(m => ({ default: m.LectureDetailPage })))
const AssignmentDetailPage = lazy(() => import('@/pages/AssignmentDetailPage').then(m => ({ default: m.AssignmentDetailPage })))

function PageFallback() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <ErrorBoundary>
          <Suspense fallback={<PageFallback />}>
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
          </Suspense>
        </ErrorBoundary>
      </ToastProvider>
    </AuthProvider>
  )
}
