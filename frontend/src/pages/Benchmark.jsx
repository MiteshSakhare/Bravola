import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { analyzeBenchmark } from '@/store/slices/benchmarkSlice'
import Card from '@/components/common/Card'
import Button from '@/components/common/Button'
import Loading from '@/components/common/Loading'
import ScoreCard from '@/components/benchmark/ScoreCard'
import { RefreshCw, TrendingUp, AlertCircle } from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

const Benchmark = () => {
  const dispatch = useDispatch()
  const { analysis, loading, error } = useSelector((state) => state.benchmark)
  const [hasAnalyzed, setHasAnalyzed] = useState(false)

  useEffect(() => {
    if (!hasAnalyzed) {
      handleAnalyze()
    }
  }, [])

  const handleAnalyze = async (forceRefresh = false) => {
    await dispatch(analyzeBenchmark(forceRefresh))
    setHasAnalyzed(true)
  }

  if (loading && !analysis) {
    return <Loading text="Running benchmark analysis..." />
  }

  const radarData = analysis?.benchmark
    ? [
        { metric: 'AOV', score: analysis.benchmark.aov_score },
        { metric: 'LTV', score: analysis.benchmark.ltv_score },
        { metric: 'Repeat Rate', score: analysis.benchmark.repeat_rate_score },
        { metric: 'Engagement', score: analysis.benchmark.engagement_score },
      ]
    : []

  return (
    <div className="space-y-8 animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Benchmark Analysis</h1>
          <p className="text-gray-600 mt-2">
            Compare your performance against industry peers
          </p>
        </div>
        <Button
          onClick={() => handleAnalyze(true)}
          disabled={loading}
          loading={loading}
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Analysis
        </Button>
      </div>

      {error && (
        <Card>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => handleAnalyze()}>Try Again</Button>
          </div>
        </Card>
      )}

      {analysis && (
        <>
          {/* Overall Score */}
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Overall Performance Score</p>
              <div className="text-6xl font-bold text-primary-600 mb-2">
                {analysis.benchmark.overall_score.toFixed(0)}
              </div>
              <p className="text-gray-600">out of 100</p>
              <p className="text-sm text-gray-500 mt-2">
                Peer Group: {analysis.benchmark.peer_group_name}
              </p>
            </div>
          </Card>

          {/* Score Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <ScoreCard
              title="Average Order Value"
              score={analysis.benchmark.aov_score}
              percentile={analysis.benchmark.aov_percentile}
            />
            <ScoreCard
              title="Customer LTV"
              score={analysis.benchmark.ltv_score}
              percentile={analysis.benchmark.ltv_percentile}
            />
            <ScoreCard
              title="Repeat Purchase Rate"
              score={analysis.benchmark.repeat_rate_score}
              percentile={analysis.benchmark.repeat_rate_percentile}
            />
            <ScoreCard
              title="Email Engagement"
              score={analysis.benchmark.engagement_score}
            />
          </div>

          {/* Radar Chart */}
          <Card title="Performance Radar">
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Your Score"
                  dataKey="score"
                  stroke="#0ea5e9"
                  fill="#0ea5e9"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Card>

          {/* Peer Comparisons */}
          {analysis.peer_comparisons?.length > 0 && (
            <Card title="Detailed Peer Comparison">
              <div className="space-y-6">
                {analysis.peer_comparisons.map((comparison, index) => (
                  <div key={index} className="border-b last:border-b-0 pb-4 last:pb-0">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{comparison.metric_name}</h4>
                      <span
                        className={`badge ${
                          comparison.status === 'above'
                            ? 'badge-success'
                            : comparison.status === 'average'
                            ? 'badge-warning'
                            : 'badge-danger'
                        }`}
                      >
                        {comparison.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Your Value</p>
                        <p className="font-medium">{comparison.your_value.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Peer 50th %</p>
                        <p className="font-medium">{comparison.peer_p50.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Peer 75th %</p>
                        <p className="font-medium">{comparison.peer_p75.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Your Percentile</p>
                        <p className="font-medium">{comparison.your_percentile.toFixed(0)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Strengths */}
          {analysis.strengths?.length > 0 && (
            <Card title="Your Strengths">
              <div className="space-y-2">
                {analysis.strengths.map((strength, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg"
                  >
                    <TrendingUp className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Improvement Opportunities */}
          {analysis.improvement_opportunities?.length > 0 && (
            <Card title="Improvement Opportunities">
              <div className="space-y-2">
                {analysis.improvement_opportunities.map((opportunity, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg"
                  >
                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{opportunity}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Action Items */}
          {analysis.action_items?.length > 0 && (
            <Card title="Recommended Actions">
              <ol className="space-y-2">
                {analysis.action_items.map((action, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <span className="w-6 h-6 rounded-full bg-primary-600 text-white flex items-center justify-center flex-shrink-0 text-sm font-medium">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{action}</span>
                  </li>
                ))}
              </ol>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

export default Benchmark
