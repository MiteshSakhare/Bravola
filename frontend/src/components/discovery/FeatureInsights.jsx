import React from 'react'
import { TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react'

const FeatureInsights = ({ features }) => {
  const getInsightIcon = (type) => {
    switch (type) {
      case 'strength':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />
      case 'opportunity':
        return <TrendingUp className="w-5 h-5 text-blue-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />
    }
  }

  const getInsightColor = (type) => {
    switch (type) {
      case 'strength':
        return 'bg-green-50 border-green-200'
      case 'opportunity':
        return 'bg-blue-50 border-blue-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-3">
      {features.map((feature, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg border ${getInsightColor(feature.type)}`}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-0.5">
              {getInsightIcon(feature.type)}
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900 mb-1">{feature.name}</h4>
              <p className="text-sm text-gray-700 mb-2">{feature.description}</p>
              {feature.value && (
                <div className="flex items-center space-x-4 text-sm">
                  <div>
                    <span className="text-gray-600">Your Value: </span>
                    <span className="font-medium">{feature.value}</span>
                  </div>
                  {feature.benchmark && (
                    <div>
                      <span className="text-gray-600">Benchmark: </span>
                      <span className="font-medium">{feature.benchmark}</span>
                    </div>
                  )}
                </div>
              )}
              {feature.recommendation && (
                <p className="text-sm text-gray-600 mt-2 italic">
                  💡 {feature.recommendation}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default FeatureInsights
