// Scheduler types
export interface Scheduler {
  id: string
  name: string
  description?: string
  job_type: JobType
  frequency: FrequencyType
  frequency_config: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at?: string
  last_run?: string
  next_run?: string
}

export interface CreateScheduler {
  name: string
  description?: string
  job_type: JobType
  frequency: FrequencyType
  frequency_config: Record<string, any>
}

export interface UpdateScheduler {
  name?: string
  description?: string
  job_type?: JobType
  frequency?: FrequencyType
  frequency_config?: Record<string, any>
  is_active?: boolean
}

// Log types
export interface Log {
  id: string
  scheduler_id: string
  job_type: string
  status: LogStatus
  message?: string
  started_at: string
  completed_at?: string
  duration?: number
}

// Statistics types
export interface Statistics {
  total_schedulers: number
  active_schedulers: number
  paused_schedulers: number
  total_executions: number
  successful_executions: number
  failed_executions: number
  executions_by_job_type: Record<string, number>
  executions_by_date: Record<string, number>
  average_execution_duration?: number
}

// Enum types
export type JobType = 
  | 'email_notification'
  | 'data_backup'
  | 'report_generation'
  | 'api_call'
  | 'file_cleanup'
  | 'custom'

export type FrequencyType = 'cron' | 'interval' | 'date'

export type LogStatus = 'success' | 'error' | 'running'

// Frequency configuration types
export interface CronConfig {
  cron_expression: string
  timezone?: string
}

export interface IntervalConfig {
  seconds?: number
  minutes?: number
  hours?: number
  days?: number
}

export interface DateConfig {
  run_date: string
}

// Helper constants
export const JOB_TYPE_LABELS: Record<JobType, string> = {
  email_notification: 'Email Notification',
  data_backup: 'Data Backup',
  report_generation: 'Report Generation',
  api_call: 'API Call',
  file_cleanup: 'File Cleanup',
  custom: 'Custom'
}

export const FREQUENCY_TYPE_LABELS: Record<FrequencyType, string> = {
  cron: 'Cron Expression',
  interval: 'Interval',
  date: 'Specific Date'
}

export const STATUS_COLORS: Record<LogStatus, string> = {
  success: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  running: 'bg-blue-100 text-blue-800'
}

export const STATUS_ICONS: Record<LogStatus, string> = {
  success: '✓',
  error: '✗',
  running: '●'
}
