import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const ScoreCard = ({ title, score, percentile, comparison }) => {
  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600'
    if (score >= 60) return 'text-blue-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getIcon = () => {
    if (score >= 60) return <TrendingUp className="w-5 h-5 text-green-500" />
    if (score >= 40) return <Minus className="w-5 h-5 text-yellow-500" />
    return <TrendingDown className="w-5 h-5 text-red-500" />
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-600">{title}</h4>
        {getIcon()}
      </div>

      <div className="mb-2">
        <span className={`text-3xl font-bold ${getScoreColor(score)}`}>
          {score.toFixed(0)}
        </span>
        <span className="text-gray-500 ml-1">/100</span>
      </div>

      <div className="text-sm text-gray-600">
        {percentile && <p>Top {(100 - percentile).toFixed(0)}% of peers</p>}
        {comparison && <p className="mt-1">{comparison}</p>}
      </div>
    </div>
  )
}

export default ScoreCard
