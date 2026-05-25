import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ErrorBoundary } from '@/components/ErrorBoundary'

const ThrowError = () => {
  throw new Error('Test error')
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>All good</div>
      </ErrorBoundary>,
    )
    expect(screen.getByText('All good')).toBeInTheDocument()
  })

  it('renders fallback UI on error', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Что-то пошло не так')).toBeInTheDocument()
    expect(screen.getByText('Обновить страницу')).toBeInTheDocument()
  })

  it('does not render children on error', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
        <div>Should not appear</div>
      </ErrorBoundary>,
    )
    expect(screen.queryByText('Should not appear')).not.toBeInTheDocument()
  })

  it('has a reload button', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>,
    )
    const button = screen.getByText('Обновить страницу')
    expect(button).toBeInTheDocument()
  })
})
