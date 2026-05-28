import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { LoginPage } from '@/pages/LoginPage'
import { BrowserRouter } from 'react-router-dom'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    loading: false,
  }),
}))

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ url: 'https://github.com/login/oauth/authorize?client_id=test' }),
      })
    ))
  })

  it('renders the login page title', () => {
    renderWithRouter(<LoginPage />)
    expect(screen.getByText('Python Engineering Course')).toBeInTheDocument()
  })

  it('shows the GitHub login button', () => {
    renderWithRouter(<LoginPage />)
    expect(screen.getByText('Продолжить с GitHub')).toBeInTheDocument()
  })

  it('shows the subtitle', () => {
    renderWithRouter(<LoginPage />)
    expect(screen.getByText('Войдите через GitHub, чтобы начать обучение')).toBeInTheDocument()
  })
})
