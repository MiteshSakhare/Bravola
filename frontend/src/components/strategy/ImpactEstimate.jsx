import React from 'react'
import { DollarSign, TrendingUp, Users, ShoppingCart } from 'lucide-react'
import { formatCurrency, formatNumber } from '@/utils/formatters'

const ImpactEstimate = ({ estimate }) => {
  const metrics = [
    {
      label: 'Revenue Impact',
      value: formatCurrency(estimate.revenue_impact),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      label: 'ROI',
      value: `${estimate.roi}%`,
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      label: 'New Customers',
      value: formatNumber(estimate.new_customers),
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      label: 'Additional Orders',
      value: formatNumber(estimate.additional_orders),
      icon: ShoppingCart,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Estimated Impact</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.label} className="text-center">
              <div className={`inline-flex p-3 rounded-lg ${metric.bgColor} mb-2`}>
                <Icon className={`w-6 h-6 ${metric.color}`} />
              </div>
              <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
              <p className="text-sm text-gray-600">{metric.label}</p>
            </div>
          )
        })}
      </div>

      {estimate.assumptions && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm font-medium text-gray-900 mb-2">Assumptions:</p>
          <ul className="text-sm text-gray-700 space-y-1">
            {estimate.assumptions.map((assumption, index) => (
              <li key={index}>• {assumption}</li>
            ))}
          </ul>
        </div>
      )}

      {estimate.confidence_level && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Confidence Level</span>
            <span className="text-sm font-medium text-gray-900">
              {estimate.confidence_level}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${estimate.confidence_level}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ImpactEstimate
