import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { DashboardPage } from '@/pages/DashboardPage'
import { BrowserRouter } from 'react-router-dom'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    loading: false,
  }),
}))

vi.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    addToast: vi.fn(),
  }),
}))

const mockDashboard = vi.hoisted(() => ({
  total_lectures: 14,
  completed_lectures: 5,
  progress_percentage: 36,
  needs_review: 2,
  avg_iterations: 1.5,
  progress_chart: [
    { lecture_number: 0, lecture_title: 'Объекты, типы, ссылки', ai_level: 1, status: 'merged', iteration_count: 1 },
    { lecture_number: 1, lecture_title: 'Циклы и управление потоком', ai_level: 2, status: 'merged', iteration_count: 2 },
    { lecture_number: 2, lecture_title: 'Последовательности', ai_level: null, status: 'open', iteration_count: 0 },
  ],
  assignments: [
    {
      id: 'a1',
      lecture_number: 1,
      lecture_title: 'Циклы и управление потоком',
      status: 'merged',
      iteration_count: 2,
      ai_level: 2,
      teacher_level: null,
      submitted_at: '2026-01-01T00:00:00Z',
      needs_teacher: false,
    },
  ],
  latest_review: {
    assignment_id: 'a1',
    lecture_number: 1,
    lecture_title: 'Циклы и управление потоком',
    predicted_level: 2,
    style_comments: 'Хороший стиль',
    clarifying_question: 'Почему выбран этот подход?',
    triggered_at: '2026-01-01T00:00:00Z',
  },
}))

vi.mock('@/services/api', () => ({
  api: {
    dashboard: {
      student: vi.fn().mockResolvedValue(mockDashboard),
    },
  },
}))

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('DashboardPage', () => {

  it('renders the dashboard title', async () => {
    renderWithRouter(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('Дашборд')).toBeInTheDocument()
    })
  })

  it('shows lecture progress', async () => {
    renderWithRouter(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument()
    })
    expect(screen.getByText('из 14')).toBeInTheDocument()
  })

  it('shows the assignments table header', async () => {
    renderWithRouter(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('История домашних заданий')).toBeInTheDocument()
    })
  })
})
