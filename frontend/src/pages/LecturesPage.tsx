import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '@/hooks/useToast'
import { api, type BlockData } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Code, Terminal, Layers } from 'lucide-react'

const blockMeta = [
  { icon: BookOpen, desc: 'Основы Python' },
  { icon: Code, desc: 'Структуры данных' },
  { icon: Terminal, desc: 'Продвинутые темы' },
  { icon: Layers, desc: 'Инструменты и практики' },
]

export function LecturesPage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [blocks, setBlocks] = useState<BlockData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.lectures.byBlock()
      .then(setBlocks)
      .catch((e) => {
        addToast({ title: 'Ошибка загрузки', description: e.message, variant: 'destructive' })
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-6 animate-pulse space-y-6">
        {[1, 2, 3, 4].map(b => (
          <div key={b}>
            <div className="h-6 w-48 bg-secondary rounded mb-3" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[1, 2, 3].map(l => <div key={l} className="h-24 bg-secondary rounded-xl" />)}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Программа курса</h2>
        <p className="text-sm text-muted-foreground mt-1">14 лекций в 4 блоках</p>
      </div>

      {blocks.map((block, idx) => {
        const meta = blockMeta[idx] || blockMeta[0]
        const Icon = meta.icon

        return (
          <section key={block.block}>
            <div className="flex items-center gap-2 mb-3">
              <Icon className="h-5 w-5 text-primary" />
              <h3 className="text-base font-medium text-foreground">
                Блок {block.block}: {block.title}
              </h3>
              <span className="text-xs text-muted-foreground ml-auto">{meta.desc}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {block.lectures.filter(l => l.number !== 99).map((lecture) => (
                <Card
                  key={lecture.id}
                  className="cursor-pointer transition-all hover:shadow-md"
                  onClick={() => navigate(`/lectures/${lecture.number}`)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-sm font-medium">
                        Лекция {lecture.number}: {lecture.title}
                      </CardTitle>
                      <Badge
                        variant={lecture.assignment_type === 'A' ? 'default' : 'secondary'}
                        className="ml-2 text-[10px]"
                      >
                        {lecture.assignment_type === 'A' ? 'Код' : 'Объяснение'}
                      </Badge>
                    </div>
                    {lecture.description && (
                      <CardDescription className="text-xs line-clamp-2">
                        {lecture.description}
                      </CardDescription>
                    )}
                  </CardHeader>
                  {lecture.topics && (
                    <CardContent>
                      <div className="flex flex-wrap gap-1">
                        {lecture.topics.split(', ').slice(0, 4).map((topic) => (
                          <span key={topic} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary/70 text-muted-foreground">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>
          </section>
        )
      })}
    </div>
  )
}
