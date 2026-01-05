import React from 'react'
import { STATUS_COLORS } from '@/utils/constants'
import { Target, Clock, TrendingUp } from 'lucide-react'
import { formatCurrency } from '@/utils/formatters'

const StrategyList = ({ strategies, onSelect }) => {
  return (
    <div className="space-y-4">
      {strategies.map((strategy) => (
        <div
          key={strategy.strategy_id || strategy.strategy_name}
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => onSelect && onSelect(strategy)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <Target className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold">{strategy.strategy_name}</h3>
                <span
                  className={`badge ${
                    STATUS_COLORS[strategy.status] || 'badge-info'
                  }`}
                >
                  {strategy.status}
                </span>
              </div>

              <p className="text-gray-600 mb-4">{strategy.description}</p>

              <div className="grid grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <div>
                    <p className="text-xs text-gray-500">Expected ROI</p>
                    <p className="font-medium">{strategy.expected_roi}%</p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-blue-500" />
                  <div>
                    <p className="text-xs text-gray-500">Timeline</p>
                    <p className="font-medium">{strategy.timeline || strategy.estimated_effort}</p>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-500">Est. Revenue</p>
                  <p className="font-medium">
                    {formatCurrency(strategy.estimated_revenue)}
                  </p>
                </div>
              </div>
            </div>

            <div className="ml-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary-600">
                  {strategy.priority_score?.toFixed(0) || 0}
                </p>
                <p className="text-xs text-gray-500">Priority</p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default StrategyList
