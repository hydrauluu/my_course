import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ThemeToggle } from '@/components/theme-toggle'
import {
  BookOpen,
  LayoutDashboard,
  LogOut,
  GraduationCap,
  Menu,
  X,
} from 'lucide-react'

const navItems = [
  { to: '/dashboard', label: 'Дашборд', icon: LayoutDashboard },
  { to: '/lectures', label: 'Лекции', icon: BookOpen },
]

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()
    : user?.github_username?.slice(0, 2).toUpperCase() || '?'

  function closeNav() {
    setSidebarOpen(false)
  }

  return (
    <div className="flex h-screen bg-background">
      <aside
        className={`
          fixed inset-y-0 left-0 z-30 w-56 flex-shrink-0 border-r border-border bg-card
          transition-transform duration-200 ease-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:relative lg:translate-x-0
        `}
      >
        <div className="flex h-14 items-center justify-between gap-2 px-5 border-b border-border">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-primary" />
            <span className="font-semibold text-sm text-foreground">Python Course</span>
          </div>
          <button
            onClick={closeNav}
            className="lg:hidden p-1 text-muted-foreground hover:text-foreground"
            aria-label="Закрыть меню"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="p-3 space-y-1" aria-label="Основная навигация">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={closeNav}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 min-h-[44px] rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground font-medium'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/30 lg:hidden"
          onClick={closeNav}
          aria-hidden="true"
        />
      )}

      <div className="flex flex-1 flex-col min-w-0">
        <header className="flex h-14 items-center justify-between px-6 border-b border-border bg-card">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-1 -ml-1 text-muted-foreground hover:text-foreground"
              aria-label="Открыть меню"
            >
              <Menu className="h-5 w-5" />
            </button>
            <h1 className="text-sm font-medium text-foreground">
              Python Engineering Course
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <span className="text-sm text-muted-foreground hidden sm:block">
              {user?.full_name || user?.github_username}
            </span>
            <Avatar className="h-10 w-10" aria-label={user?.full_name || user?.github_username || 'Пользователь'}>
              <AvatarFallback className="text-xs bg-primary text-primary-foreground">
                {initials}
              </AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="icon" onClick={() => { logout(); navigate('/login') }}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
