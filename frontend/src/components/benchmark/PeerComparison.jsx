import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const PeerComparison = ({ comparison }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'above':
        return <TrendingUp className="w-5 h-5 text-green-500" />
      case 'below':
        return <TrendingDown className="w-5 h-5 text-red-500" />
      default:
        return <Minus className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'above':
        return 'bg-green-50 border-green-200'
      case 'below':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-yellow-50 border-yellow-200'
    }
  }

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor(comparison.status)}`}>
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-gray-900">{comparison.metric_name}</h4>
        {getStatusIcon(comparison.status)}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-600">Your Value</p>
          <p className="text-lg font-semibold">{comparison.your_value.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Peer Median</p>
          <p className="text-lg font-semibold">{comparison.peer_p50.toFixed(2)}</p>
        </div>
      </div>

      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block text-primary-600">
              Percentile: {comparison.your_percentile.toFixed(0)}th
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
          <div
            style={{ width: `${comparison.your_percentile}%` }}
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-600"
          />
        </div>
      </div>

      {comparison.insight && (
        <p className="text-sm text-gray-700 mt-2">{comparison.insight}</p>
      )}
    </div>
  )
}

export default PeerComparison
