import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { MemoryRouter } from 'react-router-dom'

let mockAuth = { isAuthenticated: false, loading: false }

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => mockAuth,
}))

describe('ProtectedRoute', () => {
  it('redirects to login when not authenticated', () => {
    mockAuth = { isAuthenticated: false, loading: false }

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    )

    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })

  it('shows loading spinner while checking auth', () => {
    mockAuth = { isAuthenticated: false, loading: true }

    const { container } = render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    )

    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    mockAuth = { isAuthenticated: true, loading: false }

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    )

    expect(screen.getByText('Protected content')).toBeInTheDocument()
  })
})
