import React from 'react'
import { MATURITY_COLORS } from '@/utils/constants'
import { TrendingUp } from 'lucide-react'

const MaturityStage = ({ stage, confidence, indicators = [], nextSteps = [] }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Maturity Stage</h3>
        <span className="text-sm text-gray-500">
          {(confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <div className="mb-6">
        <span
          className={`inline-block px-4 py-2 rounded-full text-lg font-medium ${
            MATURITY_COLORS[stage] || 'bg-gray-100 text-gray-800'
          }`}
        >
          {stage}
        </span>
      </div>

      {indicators.length > 0 && (
        <div className="mb-4">
          <h4 className="font-medium text-gray-900 mb-2">Current Indicators</h4>
          <ul className="space-y-1">
            {indicators.map((indicator, index) => (
              <li key={index} className="text-sm text-gray-600">
                • {indicator}
              </li>
            ))}
          </ul>
        </div>
      )}

      {nextSteps.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-primary-600" />
            <h4 className="font-medium text-gray-900">Next Stage Requirements</h4>
          </div>
          <ul className="space-y-1">
            {nextSteps.map((step, index) => (
              <li key={index} className="text-sm text-gray-600">
                • {step}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default MaturityStage
