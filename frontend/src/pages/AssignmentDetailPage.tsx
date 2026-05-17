import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { api, type Assignment } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Github, RefreshCw, Brain, GitPullRequest, AlertCircle } from 'lucide-react'

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'secondary' | 'destructive' }> = {
  open: { label: 'Открыт', variant: 'warning' },
  needs_work: { label: 'На доработке', variant: 'destructive' },
  merged: { label: 'Принят', variant: 'success' },
  rejected: { label: 'Отклонён', variant: 'secondary' },
}

export function AssignmentDetailPage() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const { id } = useParams()
  const [assignment, setAssignment] = useState<Assignment | null>(null)
  const [loading, setLoading] = useState(true)
  const [reviewing, setReviewing] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    if (id) {
      api.assignments.get(id)
        .then(setAssignment)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [isAuthenticated, navigate, id])

  const handleTriggerReview = async () => {
    if (!id) return
    setReviewing(true)
    try {
      await api.assignments.triggerReview(id)
      const updated = await api.assignments.get(id)
      setAssignment(updated)
    } catch (e) {
      console.error(e)
    } finally {
      setReviewing(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6 animate-pulse space-y-4">
        <div className="h-6 w-24 bg-secondary rounded" />
        <div className="h-8 w-64 bg-secondary rounded" />
        <div className="h-48 bg-secondary rounded-xl" />
      </div>
    )
  }

  if (!assignment) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">Домашнее задание не найдено</p>
        <Button variant="link" onClick={() => navigate('/dashboard')}>← На дашборд</Button>
      </div>
    )
  }

  const status = statusConfig[assignment.status] || statusConfig.open
  const latestReview = assignment.reviews?.[assignment.reviews.length - 1]

  return (
    <div className="p-6 max-w-4xl mx-auto animate-fade-in">
      <Button variant="ghost" className="mb-4 gap-1 text-sm" onClick={() => navigate('/dashboard')}>
        <ArrowLeft className="h-4 w-4" />
        На дашборд
      </Button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={status.variant}>{status.label}</Badge>
            <span className="text-xs text-muted-foreground">
              {assignment.iteration_count} итераций
            </span>
          </div>
          <h2 className="text-2xl font-semibold text-foreground">Домашнее задание</h2>
        </div>

        <div className="flex items-center gap-2">
          {assignment.github_pr_url && (
            <Button variant="outline" size="sm" className="gap-1" asChild>
              <a href={assignment.github_pr_url} target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4" />
                PR на GitHub
              </a>
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            className="gap-1"
            onClick={handleTriggerReview}
            disabled={reviewing}
          >
            <RefreshCw className={`h-4 w-4 ${reviewing ? 'animate-spin' : ''}`} />
            Запустить ревью
          </Button>
        </div>
      </div>

      {assignment.branch_name && (
        <Card className="mb-6">
          <CardHeader className="py-3">
            <CardTitle className="text-xs font-medium text-muted-foreground">Ветка</CardTitle>
          </CardHeader>
          <CardContent className="py-2">
            <code className="text-sm bg-secondary px-2 py-1 rounded">{assignment.branch_name}</code>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI оценка
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assignment.ai_level !== null ? `${assignment.ai_level} / 3` : '—'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <GitPullRequest className="h-4 w-4" />
              Оценка преподавателя
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assignment.teacher_level !== null ? `${assignment.teacher_level} / 3` : 'Ожидается'}
            </div>
          </CardContent>
        </Card>
      </div>

      {assignment.needs_teacher && (
        <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg mb-6 text-sm text-amber-800">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          Это задание требует проверки преподавателем
        </div>
      )}

      {latestReview && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              AI-ревью
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {latestReview.predicted_level !== null && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Предварительный уровень</span>
                <Badge variant="default">{latestReview.predicted_level} / 3</Badge>
              </div>
            )}

            <Separator />

            {latestReview.style_comments && (
              <div className="text-sm">
                <span className="font-medium">Стиль: </span>
                {latestReview.style_comments}
              </div>
            )}

            {latestReview.logic_comments && (
              <div className="text-sm">
                <span className="font-medium">Анализ: </span>
                {latestReview.logic_comments.length > 200
                  ? latestReview.logic_comments.slice(0, 200) + '...'
                  : latestReview.logic_comments
                }
              </div>
            )}

            {latestReview.clarifying_question && (
              <div className="bg-secondary/50 rounded-lg p-3 text-sm">
                <span className="font-medium">❓ Вопрос: </span>
                {latestReview.clarifying_question}
              </div>
            )}

            {latestReview.error_occurred && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                При ревью произошла ошибка
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {assignment.pr_description && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">PR description</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm whitespace-pre-wrap bg-secondary/30 rounded-lg p-4 font-sans leading-relaxed">
              {assignment.pr_description}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
