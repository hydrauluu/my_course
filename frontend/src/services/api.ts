const API_BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || `Request failed: ${res.status}`)
  }

  return res.json()
}

export interface Lecture {
  id: string
  number: number
  title: string
  block: number
  description: string
  topics: string
  real_code_link: string | null
  assignment_type: string
  assignment_description: string | null
  content: string | null
  is_published: boolean
  lecture_date: string | null
  created_at: string
}

export interface AIReview {
  id: string
  triggered_at: string
  runs_without_errors: boolean | null
  tests_passed: string | null
  style_comments: string | null
  logic_comments: string | null
  clarifying_question: string | null
  predicted_level: number | null
  error_occurred: boolean
}

export interface Assignment {
  id: string
  lecture_id: string
  student_id: string
  github_pr_url: string | null
  branch_name: string | null
  status: string
  pr_description: string | null
  iteration_count: number
  ai_level: number | null
  teacher_level: number | null
  ai_comment: string | null
  teacher_comment: string | null
  needs_teacher: boolean
  submitted_at: string | null
  merged_at: string | null
  created_at: string
  reviews: AIReview[]
}

export interface ProgressPoint {
  lecture_number: number
  lecture_title: string
  ai_level: number | null
  status: string
  iteration_count: number
}

export interface StudentDashboard {
  total_lectures: number
  completed_lectures: number
  progress_percentage: number
  needs_review: number
  avg_iterations: number
  progress_chart: ProgressPoint[]
  assignments: Array<{
    id: string
    lecture_number: number | null
    lecture_title: string | null
    status: string
    iteration_count: number
    ai_level: number | null
    teacher_level: number | null
    submitted_at: string | null
    needs_teacher: boolean
  }>
  latest_review: {
    assignment_id: string
    lecture_number: number | null
    lecture_title: string | null
    predicted_level: number | null
    style_comments: string | null
    clarifying_question: string | null
    triggered_at: string | null
  } | null
}

export interface BlockData {
  block: number
  title: string
  lectures: Lecture[]
}

export const api = {
  lectures: {
    list: () => request<Lecture[]>('/lectures'),
    byBlock: () => request<BlockData[]>('/lectures/blocks'),
    byNumber: (n: number) => request<Lecture>(`/lectures/number/${n}`),
    get: (id: string) => request<Lecture>(`/lectures/${id}`),
  },
  assignments: {
    list: () => request<Assignment[]>('/assignments'),
    get: (id: string) => request<Assignment>(`/assignments/${id}`),
    triggerReview: (id: string) => request<{ message: string }>(`/assignments/${id}/review`, { method: 'POST' }),
  },
  dashboard: {
    student: () => request<StudentDashboard>('/dashboard/student'),
  },
  auth: {
    githubUrl: () => request<{ url: string }>('/auth/github/login'),
    me: () => request('/auth/me'),
  },
}
