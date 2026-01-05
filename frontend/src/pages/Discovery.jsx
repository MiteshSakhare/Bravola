import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { analyzeDiscovery } from '@/store/slices/discoverySlice'
import Card from '@/components/common/Card'
import Button from '@/components/common/Button'
import Loading from '@/components/common/Loading'
import PersonaCard from '@/components/discovery/PersonaCard'
import MaturityStage from '@/components/discovery/MaturityStage'
import { RefreshCw, Sparkles } from 'lucide-react'

const Discovery = () => {
  const dispatch = useDispatch()
  const { analysis, loading, error } = useSelector((state) => state.discovery)
  const [hasAnalyzed, setHasAnalyzed] = useState(false)

  useEffect(() => {
    // Auto-run on mount if not analyzed
    if (!hasAnalyzed) {
      handleAnalyze()
    }
  }, [])

  const handleAnalyze = async (forceRefresh = false) => {
    await dispatch(analyzeDiscovery(forceRefresh))
    setHasAnalyzed(true)
  }

  if (loading && !analysis) {
    return <Loading text="Running discovery analysis..." />
  }

  return (
    <div className="space-y-8 animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Discovery Analysis</h1>
          <p className="text-gray-600 mt-2">
            Understand your business persona and maturity stage
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
          {/* Main Analysis Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PersonaCard
              persona={analysis.persona_insight.persona}
              confidence={analysis.persona_insight.confidence}
              characteristics={analysis.persona_insight.characteristics}
            />

            <MaturityStage
              stage={analysis.maturity_insight.stage}
              confidence={analysis.maturity_insight.confidence}
              indicators={analysis.maturity_insight.indicators}
              nextSteps={analysis.maturity_insight.next_stage_requirements}
            />
          </div>

          {/* Strengths */}
          {analysis.persona_insight.strengths?.length > 0 && (
            <Card title="Your Strengths">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.persona_insight.strengths.map((strength, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg"
                  >
                    <Sparkles className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Growth Opportunities */}
          {analysis.persona_insight.opportunities?.length > 0 && (
            <Card title="Growth Opportunities">
              <div className="space-y-3">
                {analysis.persona_insight.opportunities.map((opportunity, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg"
                  >
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 text-sm font-medium">
                      {index + 1}
                    </div>
                    <span className="text-sm text-gray-700">{opportunity}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Recommendations */}
          {analysis.recommendations?.length > 0 && (
            <Card title="Next Steps">
              <ul className="space-y-2">
                {analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-primary-600 font-bold">→</span>
                    <span className="text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

export default Discovery
