'use client'

import { useState } from 'react'
import { Play, Pause, Trash2, Calendar, Clock, AlertCircle } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { pauseScheduler, resumeScheduler, deleteScheduler } from '@/lib/api'
import type { Scheduler } from '@/lib/types'

interface SchedulerTableProps {
  schedulers: Scheduler[]
  onAction: () => void
}

export default function SchedulerTable({ schedulers, onAction }: SchedulerTableProps) {
  const [loadingActions, setLoadingActions] = useState<Set<string>>(new Set())

  const handleAction = async (
    action: () => Promise<void>,
    schedulerId: string,
    actionName: string
  ) => {
    setLoadingActions(prev => new Set(prev).add(schedulerId))
    try {
      await action()
      onAction() // Refresh the data
    } catch (error) {
      console.error(`Failed to ${actionName} scheduler:`, error)
      alert(`Failed to ${actionName} scheduler: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoadingActions(prev => {
        const newSet = new Set(prev)
        newSet.delete(schedulerId)
        return newSet
      })
    }
  }

  const handlePause = async (id: string) => {
    await handleAction(() => pauseScheduler(id), id, 'pause')
  }

  const handleResume = async (id: string) => {
    await handleAction(() => resumeScheduler(id), id, 'resume')
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this scheduler? This action cannot be undone.')) {
      await handleAction(() => deleteScheduler(id), id, 'delete')
    }
  }

  const getJobTypeLabel = (jobType: string) => {
    const labels: Record<string, string> = {
      email_notification: 'Email Notification',
      data_backup: 'Data Backup',
      report_generation: 'Report Generation',
      api_call: 'API Call',
      file_cleanup: 'File Cleanup',
      custom: 'Custom'
    }
    return labels[jobType] || jobType
  }

  const getFrequencyLabel = (frequency: string) => {
    const labels: Record<string, string> = {
      cron: 'Cron',
      interval: 'Interval',
      date: 'One-time'
    }
    return labels[frequency] || frequency
  }

  const formatFrequencyConfig = (frequency: string, config: any) => {
    if (frequency === 'cron') {
      return config.cron_expression
    } else if (frequency === 'interval') {
      const parts = []
      if (config.days) parts.push(`${config.days}d`)
      if (config.hours) parts.push(`${config.hours}h`)
      if (config.minutes) parts.push(`${config.minutes}m`)
      if (config.seconds) parts.push(`${config.seconds}s`)
      return `Every ${parts.join(' ')}`
    } else if (frequency === 'date') {
      return format(new Date(config.run_date), 'MMM d, yyyy HH:mm')
    }
    return 'Unknown'
  }

  if (schedulers.length === 0) {
    return (
      <div className="p-12 text-center">
        <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No schedulers found</h3>
        <p className="text-gray-500">Create your first scheduler to get started.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name & Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Job Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Schedule
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Next Run
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Run
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {schedulers.map((scheduler) => (
            <tr key={scheduler.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {scheduler.name}
                  </div>
                  {scheduler.description && (
                    <div className="text-sm text-gray-500 mt-1">
                      {scheduler.description}
                    </div>
                  )}
                  <div className="mt-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        scheduler.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {scheduler.is_active ? 'Active' : 'Paused'}
                    </span>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">
                  {getJobTypeLabel(scheduler.job_type)}
                </div>
                <div className="text-sm text-gray-500">
                  {getFrequencyLabel(scheduler.frequency)}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-gray-900">
                  {formatFrequencyConfig(scheduler.frequency, scheduler.frequency_config)}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scheduler.next_run ? (
                  <div>
                    <div>{format(new Date(scheduler.next_run), 'MMM d, HH:mm')}</div>
                    <div className="text-xs text-gray-400">
                      {formatDistanceToNow(new Date(scheduler.next_run), { addSuffix: true })}
                    </div>
                  </div>
                ) : (
                  'Not scheduled'
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scheduler.last_run ? (
                  <div>
                    <div>{format(new Date(scheduler.last_run), 'MMM d, HH:mm')}</div>
                    <div className="text-xs text-gray-400">
                      {formatDistanceToNow(new Date(scheduler.last_run), { addSuffix: true })}
                    </div>
                  </div>
                ) : (
                  'Never'
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div className="flex items-center space-x-2">
                  {scheduler.is_active ? (
                    <button
                      onClick={() => handlePause(scheduler.id)}
                      disabled={loadingActions.has(scheduler.id)}
                      className="text-yellow-600 hover:text-yellow-900 disabled:opacity-50 p-1 rounded hover:bg-yellow-50"
                      title="Pause scheduler"
                    >
                      {loadingActions.has(scheduler.id) ? (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      ) : (
                        <Pause className="h-4 w-4" />
                      )}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleResume(scheduler.id)}
                      disabled={loadingActions.has(scheduler.id)}
                      className="text-green-600 hover:text-green-900 disabled:opacity-50 p-1 rounded hover:bg-green-50"
                      title="Resume scheduler"
                    >
                      {loadingActions.has(scheduler.id) ? (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(scheduler.id)}
                    disabled={loadingActions.has(scheduler.id)}
                    className="text-red-600 hover:text-red-900 disabled:opacity-50 p-1 rounded hover:bg-red-50"
                    title="Delete scheduler"
                  >
                    {loadingActions.has(scheduler.id) ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
