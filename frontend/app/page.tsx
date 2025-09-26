'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Plus, Calendar, Clock, AlertCircle } from 'lucide-react'
import SchedulerTable from '@/components/SchedulerTable'
import { getSchedulers, getStatistics } from '@/lib/api'
import type { Scheduler, Statistics } from '@/lib/types'

export default function DashboardPage() {
  const [schedulers, setSchedulers] = useState<Scheduler[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [schedulersData, statsData] = await Promise.all([
        getSchedulers(),
        getStatistics()
      ])
      setSchedulers(schedulersData)
      setStatistics(statsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleSchedulerAction = () => {
    // Reload data when an action is performed
    loadData()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Scheduler Dashboard</h1>
              <p className="text-gray-600">Manage your scheduled jobs and view execution logs</p>
            </div>
            <div className="flex space-x-4">
              <Link
                href="/logs"
                className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors inline-flex items-center"
              >
                <Clock className="h-4 w-4 mr-2" />
                View Logs
              </Link>
              <Link
                href="/add-scheduler"
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors inline-flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Scheduler
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Calendar className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Schedulers</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total_schedulers}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <div className="h-4 w-4 bg-green-500 rounded-full"></div>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.active_schedulers}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <div className="h-4 w-4 bg-yellow-500 rounded-full"></div>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Paused</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.paused_schedulers}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-8 w-8 text-purple-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Executions</p>
                  <p className="text-2xl font-bold text-purple-600">{statistics.total_executions}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Schedulers Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Active Schedulers</h2>
              <p className="text-sm text-gray-500">
                {schedulers.length} scheduler{schedulers.length !== 1 ? 's' : ''} total
              </p>
            </div>
          </div>
          <SchedulerTable 
            schedulers={schedulers} 
            onAction={handleSchedulerAction}
          />
        </div>
      </div>
    </div>
  )
}
