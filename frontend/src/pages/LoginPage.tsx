import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { GraduationCap, Github } from 'lucide-react'

export function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [githubUrl, setGitHubUrl] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    api.auth.githubUrl()
      .then(data => setGitHubUrl(data.url))
      .catch(() => setError('Failed to connect to server'))
  }, [])

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      localStorage.setItem('token', token)
      window.location.href = '/dashboard'
      return
    }
    const code = searchParams.get('code')
    if (code) {
      login(code)
        .then(() => navigate('/dashboard'))
        .catch(() => setError('Authentication failed'))
    }
  }, [searchParams])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-pulse text-primary">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="w-full max-w-sm mx-auto px-4">
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary text-primary-foreground mb-4">
            <GraduationCap className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground">
            Python Engineering Course
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            Войдите через GitHub, чтобы начать обучение
          </p>
        </div>

        <div className="animate-fade-in">
          {error && (
            <p className="text-sm text-destructive text-center mb-4">{error}</p>
          )}
          <Button
            className="w-full h-11 gap-2 text-base"
            onClick={() => window.location.href = githubUrl}
            disabled={!githubUrl}
          >
            <Github className="h-5 w-5" />
            Продолжить с GitHub
          </Button>
        </div>

        <p className="text-xs text-muted-foreground text-center mt-6">
          Нажимая кнопку, вы соглашаетесь с обработкой данных
        </p>
      </div>
    </div>
  )
}
