'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { createScheduler } from '@/lib/api'
import type { CreateScheduler } from '@/lib/types'

interface AddSchedulerFormProps {
  onSuccess: () => void
  isSubmitting: boolean
  setIsSubmitting: (submitting: boolean) => void
}

interface FormData {
  name: string
  description: string
  job_type: string
  frequency: string
  cron_expression: string
  timezone: string
  seconds: number
  minutes: number
  hours: number
  days: number
  run_date: string
}

export default function AddSchedulerForm({ onSuccess, isSubmitting, setIsSubmitting }: AddSchedulerFormProps) {
  const [selectedFrequency, setSelectedFrequency] = useState('')
  
  const { register, handleSubmit, watch, formState: { errors }, reset } = useForm<FormData>({
    defaultValues: {
      timezone: 'UTC'
    }
  })

  const watchedFrequency = watch('frequency')

  const jobTypes = [
    { value: 'email_notification', label: 'Email Notification' },
    { value: 'data_backup', label: 'Data Backup' },
    { value: 'report_generation', label: 'Report Generation' },
    { value: 'api_call', label: 'API Call' },
    { value: 'file_cleanup', label: 'File Cleanup' },
    { value: 'custom', label: 'Custom' }
  ]

  const frequencyTypes = [
    { value: 'cron', label: 'Cron Expression' },
    { value: 'interval', label: 'Interval' },
    { value: 'date', label: 'Specific Date' }
  ]

  const timezones = [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
    { value: 'Europe/London', label: 'London' },
    { value: 'Europe/Paris', label: 'Paris' },
    { value: 'Asia/Tokyo', label: 'Tokyo' }
  ]

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    
    try {
      let frequencyConfig: any = {}

      if (data.frequency === 'cron') {
        frequencyConfig = {
          cron_expression: data.cron_expression,
          timezone: data.timezone || 'UTC'
        }
      } else if (data.frequency === 'interval') {
        const config: any = {}
        if (data.seconds) config.seconds = Number(data.seconds)
        if (data.minutes) config.minutes = Number(data.minutes)
        if (data.hours) config.hours = Number(data.hours)
        if (data.days) config.days = Number(data.days)
        
        if (Object.keys(config).length === 0) {
          alert('Please specify at least one interval value')
          return
        }
        
        frequencyConfig = config
      } else if (data.frequency === 'date') {
        frequencyConfig = {
          run_date: data.run_date
        }
      }

      const schedulerData: CreateScheduler = {
        name: data.name,
        description: data.description || undefined,
        job_type: data.job_type as any,
        frequency: data.frequency as any,
        frequency_config: frequencyConfig
      }

      await createScheduler(schedulerData)
      reset()
      onSuccess()
    } catch (error) {
      console.error('Failed to create scheduler:', error)
      alert(`Failed to create scheduler: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h2 className="text-xl font-semibold text-gray-900">Scheduler Details</h2>
        <p className="text-sm text-gray-600 mt-1">Configure your scheduled job</p>
      </div>

      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Name *
        </label>
        <input
          type="text"
          id="name"
          {...register('name', { required: 'Name is required' })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter scheduler name"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          {...register('description')}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Optional description"
        />
      </div>

      {/* Job Type */}
      <div>
        <label htmlFor="job_type" className="block text-sm font-medium text-gray-700">
          Job Type *
        </label>
        <select
          id="job_type"
          {...register('job_type', { required: 'Job type is required' })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select job type</option>
          {jobTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.job_type && (
          <p className="mt-1 text-sm text-red-600">{errors.job_type.message}</p>
        )}
      </div>

      {/* Frequency Type */}
      <div>
        <label htmlFor="frequency" className="block text-sm font-medium text-gray-700">
          Frequency Type *
        </label>
        <select
          id="frequency"
          {...register('frequency', { required: 'Frequency type is required' })}
          onChange={(e) => setSelectedFrequency(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select frequency type</option>
          {frequencyTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.frequency && (
          <p className="mt-1 text-sm text-red-600">{errors.frequency.message}</p>
        )}
      </div>

      {/* Cron Configuration */}
      {watchedFrequency === 'cron' && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h3 className="text-sm font-medium text-gray-900">Cron Configuration</h3>
          
          <div>
            <label htmlFor="cron_expression" className="block text-sm font-medium text-gray-700">
              Cron Expression *
            </label>
            <input
              type="text"
              id="cron_expression"
              {...register('cron_expression', { 
                required: watchedFrequency === 'cron' ? 'Cron expression is required' : false 
              })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="0 9 * * * (every day at 9 AM)"
            />
            <p className="mt-1 text-xs text-gray-500">
              Format: second minute hour day month weekday
            </p>
            {errors.cron_expression && (
              <p className="mt-1 text-sm text-red-600">{errors.cron_expression.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">
              Timezone
            </label>
            <select
              id="timezone"
              {...register('timezone')}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {timezones.map((tz) => (
                <option key={tz.value} value={tz.value}>
                  {tz.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Interval Configuration */}
      {watchedFrequency === 'interval' && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h3 className="text-sm font-medium text-gray-900">Interval Configuration</h3>
          <p className="text-xs text-gray-600">Specify at least one interval value:</p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="seconds" className="block text-sm font-medium text-gray-700">
                Seconds
              </label>
              <input
                type="number"
                id="seconds"
                min="1"
                {...register('seconds')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="minutes" className="block text-sm font-medium text-gray-700">
                Minutes
              </label>
              <input
                type="number"
                id="minutes"
                min="1"
                {...register('minutes')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="hours" className="block text-sm font-medium text-gray-700">
                Hours
              </label>
              <input
                type="number"
                id="hours"
                min="1"
                {...register('hours')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label htmlFor="days" className="block text-sm font-medium text-gray-700">
                Days
              </label>
              <input
                type="number"
                id="days"
                min="1"
                {...register('days')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Date Configuration */}
      {watchedFrequency === 'date' && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h3 className="text-sm font-medium text-gray-900">Date Configuration</h3>
          
          <div>
            <label htmlFor="run_date" className="block text-sm font-medium text-gray-700">
              Run Date & Time *
            </label>
            <input
              type="datetime-local"
              id="run_date"
              {...register('run_date', { 
                required: watchedFrequency === 'date' ? 'Run date is required' : false 
              })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            {errors.run_date && (
              <p className="mt-1 text-sm text-red-600">{errors.run_date.message}</p>
            )}
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Creating...' : 'Create Scheduler'}
        </button>
      </div>
    </form>
  )
}
