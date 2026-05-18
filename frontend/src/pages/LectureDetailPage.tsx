import { useEffect, useState, useMemo, useRef, isValidElement, type ReactNode } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { cafeCodeTheme } from '@/styles/cafe-code-theme'
import { useAuth } from '@/hooks/useAuth'
import { api, type Lecture } from '@/services/api'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, BookOpen, Github, Code, FileText, ChevronLeft, ChevronRight, List } from 'lucide-react'
import { cn } from '@/lib/utils'

function getTextFromChildren(children: ReactNode): string {
  if (typeof children === 'string' || typeof children === 'number') return String(children)
  if (Array.isArray(children)) return children.map(getTextFromChildren).join('')
  if (isValidElement(children)) return getTextFromChildren(children.props.children)
  return ''
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-zа-яё0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function preprocessAdmonitions(md: string): string {
  const labelMap: Record<string, string> = {
    quote: 'Цитата',
    note: 'Примечание',
    warning: 'Внимание',
    danger: 'Важно',
  }

  return md.replace(/^!!!\s+(\w+)\s+"([^"]*)"\s*\n((?:[ \t]+.*\n*|\n)+)/gm, (_match, type, title, content) => {
    const label = title || labelMap[type.toLowerCase()] || type
    const lines = content.split('\n')
    const nonEmptyLines = lines.filter((l: string) => l.trim().length > 0)
    const minIndent = nonEmptyLines.length > 0
      ? Math.min(...nonEmptyLines.map((l: string) => l.match(/^[ \t]*/)![0].length))
      : 0
    const dedented = lines
      .map((l: string) => l.slice(minIndent))
      .join('\n')
      .trim()
    return `> **${label}**\n>\n${dedented.split('\n').map((line: string) => `> ${line}`).join('\n')}\n`
  })
}

interface TocEntry {
  level: number
  text: string
  id: string
}

export function LectureDetailPage() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const { number } = useParams()
  const [lecture, setLecture] = useState<Lecture | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeHeading, setActiveHeading] = useState('')
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    history.scrollRestoration = 'manual'
  }, [])

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    if (number !== undefined) {
      setLoading(true)
      setLecture(null)
      setActiveHeading('')
      api.lectures.byNumber(parseInt(number))
        .then(setLecture)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [isAuthenticated, authLoading, navigate, number])

  useEffect(() => {
    if (lecture) {
      requestAnimationFrame(() => window.scrollTo(0, 0))
    }
  }, [lecture])

  const contentWithoutTitle = useMemo(() => {
    if (!lecture?.content) return ''
    return preprocessAdmonitions(lecture.content.replace(/^#\s+.*(?:\n|$)/, '').trimStart())
  }, [lecture?.content])

  const toc = useMemo<TocEntry[]>(() => {
    const entries: TocEntry[] = []
    const lines = contentWithoutTitle.split('\n')
    for (const line of lines) {
      const h2 = line.match(/^##\s+(.+)/)
      const h3 = line.match(/^###\s+(.+)/)
      if (h2) entries.push({ level: 2, text: h2[1], id: slugify(h2[1]) })
      else if (h3) entries.push({ level: 3, text: h3[1], id: slugify(h3[1]) })
    }
    return entries
  }, [contentWithoutTitle])

  useEffect(() => {
    if (!toc.length) return
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setActiveHeading(e.target.id)
            break
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px' }
    )
    for (const entry of toc) {
      const el = document.getElementById(entry.id)
      if (el) observer.observe(el)
    }
    return () => observer.disconnect()
  }, [toc])

  if (loading) {
    return (
      <div className="p-6 animate-pulse space-y-4">
        <div className="h-6 w-24 bg-secondary rounded" />
        <div className="h-8 w-96 bg-secondary rounded" />
        <div className="h-64 bg-secondary rounded-xl" />
        <div className="h-96 bg-secondary rounded-xl" />
      </div>
    )
  }

  if (!lecture) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">Лекция не найдена</p>
        <Button variant="link" onClick={() => navigate('/lectures')}>← Назад к лекциям</Button>
      </div>
    )
  }

  const hasContent = contentWithoutTitle.length > 50

  function renderContent() {
    if (!hasContent) return null

    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h2: ({ children, ...props }) => {
            const text = String(children)
            const id = slugify(text)
            return (
              <h2 id={id} className="scroll-mt-20 text-xl font-semibold text-foreground mt-10 mb-4 border-b border-border pb-2">
                <a href={`#${id}`} className="hover:text-primary transition-colors">
                  {children}
                </a>
              </h2>
            )
          },
          h3: ({ children }) => {
            const text = String(children)
            const id = slugify(text)
            return (
              <h3 id={id} className="scroll-mt-20 text-lg font-medium text-foreground mt-6 mb-2">
                <a href={`#${id}`} className="hover:text-primary transition-colors">
                  {children}
                </a>
              </h3>
            )
          },
          h1: ({ children }) => (
            <h1 className="text-2xl font-semibold text-foreground mt-8 mb-4">{children}</h1>
          ),
          p: ({ children }) => (
            <p className="text-base leading-relaxed text-foreground/90 mb-4">{children}</p>
          ),
          blockquote: ({ children }) => {
            const textContent = getTextFromChildren(children)
            const isAdmonition = /Цитата|Примечание|Внимание|Важно/.test(textContent)
            if (isAdmonition) {
              const typeMatch = textContent.match(/Цитата|Примечание|Внимание|Важно/)
              const type = typeMatch ? typeMatch[0] : ''
              const styleMap: Record<string, { border: string; bg: string; iconBg: string; iconText: string }> = {
                'Цитата': { border: 'border-l-4 border-primary/40', bg: 'bg-primary/5', iconBg: 'bg-primary/10', iconText: 'text-primary' },
                'Примечание': { border: 'border-l-4 border-blue-400/50', bg: 'bg-blue-500/5', iconBg: 'bg-blue-500/10', iconText: 'text-blue-500' },
                'Внимание': { border: 'border-l-4 border-amber-400/50', bg: 'bg-amber-500/5', iconBg: 'bg-amber-500/10', iconText: 'text-amber-500' },
                'Важно': { border: 'border-l-4 border-red-400/50', bg: 'bg-red-500/5', iconBg: 'bg-red-500/10', iconText: 'text-red-500' },
              }
              const s = styleMap[type] || styleMap['Цитата']
              return (
                <blockquote className={`my-4 rounded-r-lg ${s.border} ${s.bg} [&>p:first-child]:font-semibold [&>p:first-child]:text-sm [&>p:first-child]:text-foreground/80 [&>p:first-child]:mb-2 [&>p:first-child]:border-b [&>p:first-child]:border-current/10 [&>p:first-child]:pb-2`}>
                  <div className="px-4 pt-3 pb-2">
                    {children}
                  </div>
                </blockquote>
              )
            }
            return (
              <blockquote className="border-l-4 border-primary/30 pl-4 py-3 my-4 bg-secondary/30 rounded-r-lg text-sm text-muted-foreground">
                {children}
              </blockquote>
            )
          },
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '')
            const codeStr = String(children).replace(/\n$/, '')
            if (match) {
              return (
                <SyntaxHighlighter
                  style={cafeCodeTheme}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{ margin: '1rem 0', borderRadius: '12px', fontSize: '0.875rem' }}
                >
                  {codeStr}
                </SyntaxHighlighter>
              )
            }
            return (
              <code className="bg-secondary/60 text-foreground px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            )
          },
          pre: ({ children }) => (
            <pre className="bg-secondary/60 rounded-xl p-4 overflow-x-auto my-4 text-sm font-mono leading-relaxed text-foreground/90">
              {children}
            </pre>
          ),
          ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-1.5 text-foreground/90">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-1.5 text-foreground/90">{children}</ol>,
          li: ({ children }) => <li className="text-base leading-relaxed">{children}</li>,
          a: ({ href, children }) => (
            <a
              href={href}
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
              className="text-primary underline underline-offset-4 hover:text-primary/80"
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-4 rounded-xl border border-border">
              <table className="min-w-full border-collapse text-sm">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border-r border-border bg-secondary/50 px-4 py-2.5 text-left font-medium last:border-r-0">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-r border-border border-t border-t-border px-4 py-2 last:border-r-0">
              {children}
            </td>
          ),
          hr: () => <Separator className="my-8" />,
          img: ({ src, alt }) => (
            <img src={src} alt={alt || ''} className="max-w-full rounded-xl my-4" loading="lazy" />
          ),
          strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
        }}
      >
        {contentWithoutTitle}
      </ReactMarkdown>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-8">
        <div className="flex-1 min-w-0 max-w-4xl">
          <Button variant="ghost" className="mb-4 gap-1 text-sm" onClick={() => navigate('/lectures')}>
            <ArrowLeft className="h-4 w-4" />
            К списку лекций
          </Button>

          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">Блок {lecture.block}</Badge>
              <Badge variant={lecture.assignment_type === 'A' ? 'default' : 'secondary'}>
                {lecture.assignment_type === 'A' ? (
                  <><Code className="h-3 w-3 mr-1" />Тип A — Код</>
                ) : (
                  <><FileText className="h-3 w-3 mr-1" />Тип B — Объяснение</>
                )}
              </Badge>
            </div>
            <h1 className="text-2xl font-semibold text-foreground">
              Лекция {lecture.number}: {lecture.title}
            </h1>
            {lecture.description && (
              <p className="text-sm text-muted-foreground mt-2">{lecture.description}</p>
            )}
          </div>

          {toc.length > 0 && (
            <div className="md:hidden mb-6">
              <details className="bg-card border border-border rounded-xl">
                <summary className="flex items-center gap-2 px-4 py-3 text-sm font-medium cursor-pointer">
                  <List className="h-4 w-4" />
                  Содержание лекции
                </summary>
                <div className="px-4 pb-3 space-y-1">
                  {toc.map((entry) => (
                    <a
                      key={entry.id}
                      href={`#${entry.id}`}
                      className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                      style={{ paddingLeft: entry.level === 3 ? '1rem' : '0' }}
                    >
                      {entry.text}
                    </a>
                  ))}
                </div>
              </details>
            </div>
          )}

          {hasContent && (
            <div ref={contentRef} className="prose-custom mb-8">
              {renderContent()}
            </div>
          )}

          {!hasContent && (
            <Card className="mb-6">
              <CardContent className="pt-6 text-center py-12">
                <BookOpen className="h-12 w-12 text-muted-foreground/40 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">Содержание лекции пока не загружено</p>
              </CardContent>
            </Card>
          )}

          {lecture.real_code_link && (
            <Card className="mb-6">
              <CardContent className="pt-6">
                <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-2">
                  <Github className="h-4 w-4" />
                  Ссылка на реальный код
                </h4>
                <a
                  href={lecture.real_code_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary underline underline-offset-4 hover:text-primary/80"
                >
                  {lecture.real_code_link}
                </a>
              </CardContent>
            </Card>
          )}

          <div className="flex items-center justify-between mt-8 py-4 border-t border-border">
            {lecture.number > 0 ? (
              <Button variant="outline" size="sm" onClick={() => navigate(`/lectures/${lecture.number - 1}`)}>
                <ChevronLeft className="h-4 w-4 mr-1" />
                Лекция {lecture.number - 1}
              </Button>
            ) : <div />}
            <span className="text-xs text-muted-foreground">{lecture.number} / 13</span>
            {lecture.number < 13 ? (
              <Button variant="outline" size="sm" onClick={() => navigate(`/lectures/${lecture.number + 1}`)}>
                Лекция {lecture.number + 1}
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : <div />}
          </div>
        </div>

        {toc.length > 0 && (
          <aside className="hidden md:block w-56 flex-shrink-0">
            <div className="sticky top-6">
              <div className="flex items-center gap-2 mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                <List className="h-3.5 w-3.5" />
                На странице
              </div>
              <nav className="space-y-1">
                {toc.map((entry) => (
                  <a
                    key={entry.id}
                    href={`#${entry.id}`}
                    onClick={(e) => {
                      e.preventDefault()
                      document.getElementById(entry.id)?.scrollIntoView({ behavior: 'smooth' })
                    }}
                    className={cn(
                      'block text-sm py-1 border-l-2 pl-3 transition-colors',
                      activeHeading === entry.id
                        ? 'border-primary text-foreground font-medium'
                        : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border',
                      entry.level === 3 && 'pl-6 text-xs'
                    )}
                  >
                    {entry.text}
                  </a>
                ))}
              </nav>
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}
