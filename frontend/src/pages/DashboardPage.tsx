import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { api, type StudentDashboard } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  BookOpen,
  GitPullRequest,
  Brain,
  AlertCircle,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  RefreshCw,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react'

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'secondary' | 'destructive' }> = {
  open: { label: 'Открыт', variant: 'warning' },
  needs_work: { label: 'На доработке', variant: 'destructive' },
  merged: { label: 'Принят', variant: 'success' },
  rejected: { label: 'Отклонён', variant: 'secondary' },
  pending: { label: 'Ожидает', variant: 'secondary' },
}

const levelLabels = ['', 'Синтаксис', 'Операции', 'Цель', 'Контекст']

function BarChart({ data }: { data: { label: string; value: number | null; idx: number }[] }) {
  const maxVal = 3
  const barW = Math.max(12, Math.min(28, 480 / data.length))

  return (
    <div className="w-full overflow-x-auto">
      <svg width={Math.max(data.length * (barW + 8) + 40, 320)} height="200" className="block">
        <line x1="40" y1="172" x2={Math.max(data.length * (barW + 8) + 30, 310)} y2="172" stroke="#E9E3DD" />

        {[0, 1, 2, 3].map((lv) => {
          const y = 172 - (lv / maxVal) * 140
          return (
            <g key={lv}>
              <text x="36" y={y + 4} textAnchor="end" className="fill-muted-foreground" fontSize="11">
                {lv}
              </text>
              <line x1="40" y1={y} x2={Math.max(data.length * (barW + 8) + 30, 310)} y2={y} stroke="#E9E3DD" strokeDasharray="4 4" opacity="0.4" />
            </g>
          )
        })}

        {data.map((d, i) => {
          const x = 52 + i * (barW + 8)
          const h = d.value !== null ? (d.value / maxVal) * 140 : 0
          const y = 172 - h
          const color = d.value === null ? '#E9E3DD'
            : d.value >= 3 ? '#5D7A4A'
            : d.value >= 2 ? '#5D4432'
            : d.value >= 1 ? '#B8754A'
            : '#B53A2A'

          return (
            <g key={i}>
              <rect x={x} y={y} width={barW} height={h || 4} rx="4" fill={color} opacity={d.value === null ? 0.3 : 0.85} />
              {i % 2 === 0 && (
                <text x={x + barW / 2} y="188" textAnchor="middle" className="fill-muted-foreground" fontSize="10">
                  {d.label}
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}

export function DashboardPage() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    api.dashboard.student()
      .then(setDashboard)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [isAuthenticated, navigate])

  if (loading) {
    return (
      <div className="p-6 animate-pulse space-y-5">
        <div className="h-8 w-48 bg-secondary rounded-lg" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-secondary rounded-xl" />)}
        </div>
        <div className="h-64 bg-secondary rounded-xl" />
        <div className="h-48 bg-secondary rounded-xl" />
      </div>
    )
  }

  if (!dashboard) return null

  const latestReview = dashboard.latest_review

  const kpiDelta = (current: number, total: number) => {
    if (total === 0) return { text: '—', icon: Minus, color: 'text-muted-foreground' }
    const pct = Math.round(current / total * 100)
    if (pct > 50) return { text: `${pct}%`, icon: ArrowUpRight, color: 'text-emerald-600' }
    if (pct > 20) return { text: `${pct}%`, icon: TrendingUp, color: 'text-amber-600' }
    return { text: `${pct}%`, icon: ArrowDownRight, color: 'text-red-600' }
  }

  const progressDelta = kpiDelta(dashboard.completed_lectures, dashboard.total_lectures)

  const chartData = dashboard.progress_chart.map((p, i) => ({
    label: String(p.lecture_number),
    value: p.ai_level,
    idx: i,
  }))

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Дашборд</h2>
          <p className="text-sm text-muted-foreground mt-0.5">Обзор твоего прогресса на курсе</p>
        </div>
        <button
          onClick={() => { setLoading(true); api.dashboard.student().then(setDashboard).catch(console.error).finally(() => setLoading(false)) }}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Обновить
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Лекции</CardTitle>
            <BookOpen className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold text-foreground">{dashboard.completed_lectures}</span>
              <span className="text-sm text-muted-foreground">/ {dashboard.total_lectures}</span>
            </div>
            <Progress value={dashboard.progress_percentage} className="mt-3" />
            <div className="flex items-center gap-1 mt-2">
              <progressDelta.icon className={`h-3.5 w-3.5 ${progressDelta.color}`} />
              <span className={`text-xs ${progressDelta.color}`}>{progressDelta.text} завершено</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">ДЗ сдано</CardTitle>
            <GitPullRequest className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold text-foreground">{dashboard.assignments.length}</span>
              <span className="text-sm text-muted-foreground">работ</span>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
              <span className="text-xs text-emerald-600">{dashboard.assignments.filter(a => a.status === 'merged').length} принято</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Уровень</CardTitle>
            <Brain className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold text-foreground">
                {latestReview?.predicted_level ?? '—'}
              </span>
              <span className="text-sm text-muted-foreground">/ 3</span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {latestReview?.predicted_level !== null && latestReview?.predicted_level !== undefined
                ? levelLabels[latestReview.predicted_level] || 'Нет данных'
                : 'Пока нет оценок'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Итераций</CardTitle>
            <TrendingUp className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold text-foreground">{dashboard.avg_iterations}</span>
              <span className="text-sm text-muted-foreground">среднее</span>
            </div>
            {dashboard.needs_review > 0 && (
              <div className="flex items-center gap-1 mt-2">
                <AlertCircle className="h-3.5 w-3.5 text-amber-600" />
                <span className="text-xs text-amber-600">{dashboard.needs_review} требуют проверки</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Динамика уровня понимания</CardTitle>
              <span className="text-[10px] text-muted-foreground">по лекциям · шкала 0–3</span>
            </div>
          </CardHeader>
          <CardContent>
            {chartData.some(d => d.value !== null) ? (
              <BarChart data={chartData} />
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <Brain className="h-10 w-10 mb-3 opacity-40" />
                <p className="text-sm">Пока нет данных для графика</p>
                <p className="text-xs mt-1">Сдай первое ДЗ — появится динамика</p>
              </div>
            )}
          </CardContent>
        </Card>

        {latestReview && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Последнее ревью</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  {latestReview.lecture_title || `Лекция ${latestReview.lecture_number}`}
                </span>
                <Badge variant="default" className="text-[10px]">
                  {latestReview.predicted_level ?? '?'} / 3
                </Badge>
              </div>
              {latestReview.style_comments && (
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {latestReview.style_comments}
                </p>
              )}
              {latestReview.clarifying_question && (
                <div className="bg-secondary/50 rounded-lg p-3 text-xs">
                  <span className="font-medium text-foreground flex items-center gap-1 mb-1">
                    <HelpCircle className="h-3 w-3" />
                    Вопрос
                  </span>
                  {latestReview.clarifying_question}
                </div>
              )}
              <button
                onClick={() => navigate(`/assignments/${latestReview.assignment_id}`)}
                className="text-xs text-primary underline underline-offset-4 hover:text-primary/80"
              >
                Подробнее →
              </button>
            </CardContent>
          </Card>
        )}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">История домашних заданий</CardTitle>
            <span className="text-[10px] text-muted-foreground">{dashboard.assignments.length} работ</span>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {dashboard.assignments.length === 0 ? (
            <div className="p-6 text-center text-sm text-muted-foreground">
              <GitPullRequest className="h-8 w-8 mx-auto mb-2 opacity-40" />
              Домашних заданий пока нет
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Лекция</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
                    <th className="text-center px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Итерации</th>
                    <th className="text-center px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">AI</th>
                    <th className="text-center px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Препод.</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-muted-foreground uppercase tracking-wider"></th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.assignments.map((a) => {
                    const status = statusConfig[a.status] || statusConfig.pending
                    return (
                      <tr key={a.id} className="border-b border-border hover:bg-secondary/30 transition-colors">
                        <td className="px-4 py-3 text-sm">
                          {a.lecture_title
                            ? <span className="truncate max-w-[200px] block">{a.lecture_title}</span>
                            : <span className="text-muted-foreground">—</span>
                          }
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={status.variant} className="text-[10px]">{status.label}</Badge>
                        </td>
                        <td className="px-4 py-3 text-center text-muted-foreground">{a.iteration_count}</td>
                        <td className="px-4 py-3 text-center">
                          {a.ai_level !== null
                            ? <Badge variant="secondary" className="text-[10px]">{a.ai_level}</Badge>
                            : <span className="text-muted-foreground text-xs">—</span>
                          }
                        </td>
                        <td className="px-4 py-3 text-center">
                          {a.teacher_level !== null
                            ? <Badge variant="secondary" className="text-[10px]">{a.teacher_level}</Badge>
                            : <span className="text-muted-foreground text-xs">—</span>
                          }
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => navigate(`/assignments/${a.id}`)}
                            className="text-xs text-primary underline underline-offset-4 hover:text-primary/80"
                          >
                            Открыть
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
