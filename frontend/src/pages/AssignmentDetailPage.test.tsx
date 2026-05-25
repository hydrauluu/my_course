import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { AssignmentDetailPage } from '@/pages/AssignmentDetailPage'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    loading: false,
    login: vi.fn(),
  }),
}))

vi.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    addToast: vi.fn(),
  }),
}))

const mockAssignment = {
  id: 'a1',
  lecture_id: 'l1',
  student_id: 's1',
  github_pr_url: 'https://github.com/test/repo/pull/1',
  branch_name: 'hw01/testuser',
  status: 'merged',
  pr_description: 'This is my homework submission',
  iteration_count: 2,
  ai_level: 2,
  teacher_level: null,
  ai_comment: null,
  teacher_comment: null,
  needs_teacher: false,
  submitted_at: '2026-01-01T00:00:00Z',
  merged_at: null,
  created_at: '2026-01-01T00:00:00Z',
  reviews: [
    {
      id: 'r1',
      triggered_at: '2026-01-01T01:00:00Z',
      runs_without_errors: true,
      tests_passed: '3/3',
      style_comments: 'Хороший стиль кода',
      logic_comments: 'Логика верная',
      clarifying_question: 'Почему выбран этот подход?',
      predicted_level: 2,
      error_occurred: false,
    },
  ],
}

let mockGetAssignment = vi.fn()

vi.mock('@/services/api', () => ({
  api: {
    assignments: {
      get: (...args: unknown[]) => mockGetAssignment(...args),
    },
  },
}))

function renderWithRouter(id = 'a1') {
  return render(
    <MemoryRouter initialEntries={[`/assignments/${id}`]}>
      <Routes>
        <Route path="/assignments/:id" element={<AssignmentDetailPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('AssignmentDetailPage', () => {
  it('shows loading state initially', () => {
    mockGetAssignment = vi.fn(() => new Promise(() => {}))
    renderWithRouter()
  })

  it('shows assignment data', async () => {
    mockGetAssignment = vi.fn().mockResolvedValue(mockAssignment)

    renderWithRouter()
    const scores = await screen.findAllByText(/2 \/ 3/)
    expect(scores.length).toBeGreaterThanOrEqual(1)
  })

  it('shows AI review details', async () => {
    mockGetAssignment = vi.fn().mockResolvedValue(mockAssignment)

    renderWithRouter()
    await waitFor(() => {
      expect(screen.getByText('AI-ревью')).toBeInTheDocument()
    })
    expect(screen.getByText('AI оценка')).toBeInTheDocument()
    expect(screen.getByText('Оценка преподавателя')).toBeInTheDocument()
  })

  it('shows PR description', async () => {
    mockGetAssignment = vi.fn().mockResolvedValue(mockAssignment)

    renderWithRouter()
    await waitFor(() => {
      expect(screen.getByText('PR description')).toBeInTheDocument()
    })
    expect(screen.getByText('This is my homework submission')).toBeInTheDocument()
  })

  it('shows not found when assignment errors', async () => {
    mockGetAssignment = vi.fn().mockRejectedValue(new Error('Not found'))

    renderWithRouter()
    await waitFor(() => {
      expect(screen.getByText('Домашнее задание не найдено')).toBeInTheDocument()
    })
  })

  it('shows branch name', async () => {
    mockGetAssignment = vi.fn().mockResolvedValue(mockAssignment)

    renderWithRouter()
    await waitFor(() => {
      expect(screen.getByText('hw01/testuser')).toBeInTheDocument()
    })
  })
})
