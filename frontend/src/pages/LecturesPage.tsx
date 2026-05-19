import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '@/hooks/useToast'
import { api, type BlockData } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Code, FileText } from 'lucide-react'

const blockColors = [
  { border: 'border-l-[#C4A882] dark:border-l-[#8B7355]', bg: 'bg-[#F5EDE4] dark:bg-[#2A2218]', badge: 'bg-[#E8D9C8] dark:bg-[#3D3225] text-[#6B5240] dark:text-[#C4A882]' },
  { border: 'border-l-[#A68B6B] dark:border-l-[#7A5F45]', bg: 'bg-[#EDE3D7] dark:bg-[#251E15]', badge: 'bg-[#D9C8B2] dark:bg-[#362B1E] text-[#5C4433] dark:text-[#A68B6B]' },
  { border: 'border-l-[#8B6F55] dark:border-l-[#6B4F35]', bg: 'bg-[#E5D8CB] dark:bg-[#201A12]', badge: 'bg-[#C9B49C] dark:bg-[#2F2418] text-[#4D3627] dark:text-[#8B6F55]' },
  { border: 'border-l-[#6B5240] dark:border-l-[#5C4433]', bg: 'bg-[#DDD0C2] dark:bg-[#1B1510]', badge: 'bg-[#B89F86] dark:bg-[#281E14] text-[#3E2B1E] dark:text-[#6B5240]' },
]

const blockIcons = [BookOpen, BookOpen, Code, FileText]

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
        const Icon = blockIcons[idx] || BookOpen
        const colors = blockColors[idx] || blockColors[0]

        return (
          <section key={block.block}>
            <div className="flex items-center gap-2 mb-3">
              <Icon className="h-5 w-5 text-foreground" />
              <h3 className="text-base font-medium text-foreground">
                Блок {block.block}: {block.title}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {block.lectures.map((lecture) => (
                <Card
                  key={lecture.id}
                  className={`cursor-pointer transition-all hover:shadow-md border-l-4 ${colors.border}`}
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
                          <span key={topic} className={`text-[10px] px-1.5 py-0.5 rounded ${colors.badge}`}>
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
