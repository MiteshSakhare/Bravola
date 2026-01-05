import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'

// ✅ USE NEW ACTIONS (Connected to backend)
import { fetchMerchantProfile } from '@/store/slices/merchantSlice'
import { fetchStrategies } from '@/store/slices/strategySlice'

// ✅ USE YOUR EXISTING COMPONENTS (Safe Imports)
import Card from '@/components/common/Card'
import Loading from '@/components/common/Loading'
import Button from '@/components/common/Button'

// ✅ NEW COMPONENT (For AI Strategy)
// If this import fails, check if ActionCard.jsx is in src/components/strategy/
import ActionCard from '@/components/strategy/ActionCard'

import {
  TrendingUp,
  Users,
  ShoppingCart,
  DollarSign,
  Target,
  BarChart3,
  Search,
} from 'lucide-react'
import { formatCurrency, formatNumber } from '@/utils/formatters'

const Dashboard = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  
  // ✅ Data Selectors (Updated for new Slice structure)
  const { profile, loading: merchantLoading } = useSelector((state) => state.merchant)
  const { items: strategies, loading: strategyLoading } = useSelector((state) => state.strategy)

  useEffect(() => {
    // Fetch data using new API endpoints
    dispatch(fetchMerchantProfile())
    dispatch(fetchStrategies({ limit: 3 }))
  }, [dispatch])

  if (merchantLoading || !profile) {
    return <Loading text="Loading dashboard..." />
  }

  // ✅ Data Mapping (Connect new API data to your Old UI variables)
  const currentMerchant = profile
  const metrics = profile.metrics || {}
  // Safely handle discovery/benchmark data if it exists in profile
  const discoveryProfile = profile.discovery_profile || null 
  const benchmarkScores = profile.benchmark_scores || null

  const statCards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(metrics.total_revenue || currentMerchant.monthly_revenue || 0),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Active Customers',
      value: formatNumber(metrics.active_customers || currentMerchant.total_customers || 0),
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Campaign ROI',
      value: `${metrics.campaign_roi || 0}x`,
      icon: ShoppingCart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Avg Order Value',
      value: formatCurrency(metrics.average_order_value || currentMerchant.aov || 0),
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  const handleFeedback = async (strategyId, helpful) => {
  try {
    await dispatch(submitFeedback({ strategy_id: strategyId, helpful }));
    // Optional: Refresh strategies after feedback
    dispatch(fetchStrategies());
  } catch (err) {
    console.error("Feedback failed", err);
  }
};

  return (
    <div className="space-y-8 animate-slide-in">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {currentMerchant?.shop_name || 'Merchant'}!
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mt-2">
            Here's what's happening with your business today
          </p>
        </div>
        {/* Status Badge */}
        <div className="flex gap-2">
            {profile.shopify_connected && (
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">
                    Shopify Live
                </span>
            )}
             {profile.klaviyo_connected && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold">
                    Klaviyo Active
                </span>
            )}
        </div>
      </div>

      {/* Stats Grid (Restored) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-slate-400 mb-1">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Business Insights (Restored) */}
        <div className="lg:col-span-2 space-y-6">
            <Card title="Business Insights">
                <div className="space-y-4">
                
                {/* Discovery Section */}
                <div className="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Search className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                        <p className="font-medium text-gray-900 dark:text-white">Your Business Persona</p>
                        <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">
                            You are identified as a <span className="font-bold">{discoveryProfile?.persona || profile.persona || 'Growth Merchant'}</span> in the <span className="font-bold">{discoveryProfile?.maturity_stage || profile.maturity_stage || 'Scaling'}</span> stage.
                        </p>
                    </div>
                </div>

                {/* Benchmark Section */}
                <div className="flex items-start space-x-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-green-600 mt-0.5" />
                    <div>
                        <p className="font-medium text-gray-900 dark:text-white">Performance vs Peers</p>
                        <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">
                           Your overall score is <span className="font-bold">{Math.round(benchmarkScores?.overall_score || 0)}/100</span>.
                           {(benchmarkScores?.overall_score || 0) > 50 
                             ? " You are performing above average for your sector."
                             : " There is significant room for optimization."}
                        </p>
                    </div>
                </div>

                <div className="flex justify-start space-x-4 pt-2">
                    <Button onClick={() => navigate('/discovery')}>View Analysis</Button>
                    <Button variant="outline" onClick={() => navigate('/benchmark')}>View Benchmarks</Button>
                </div>
                </div>
            </Card>

            {/* AI Strategies Section (New Feature) */}
            <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary-600" />
                    AI Recommendations
                </h3>
                <div className="space-y-4">
                    {strategyLoading ? (
                        <Loading text="Generating strategies..." />
                    ) : strategies.length > 0 ? (
                        strategies.slice(0, 3).map(strategy => (
                            <ActionCard key={strategy.strategy_id} strategy={strategy} />
                        ))
                    ) : (
                        <div className="p-8 text-center bg-gray-50 dark:bg-slate-800 rounded-lg border border-dashed border-gray-300">
                            <p className="text-gray-500">No active strategies.</p>
                            <Button className="mt-2" onClick={() => navigate('/strategy')}>Generate New Strategies</Button>
                        </div>
                    )}
                </div>
            </div>
        </div>

        {/* Right Column: Key Metrics (Restored) */}
        <div className="space-y-6">
             <Card title="Key Metrics">
                <div className="space-y-6">
                <div>
                    <p className="text-sm text-gray-600 dark:text-slate-400 mb-1">Repeat Purchase Rate</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {currentMerchant.repeat_purchase_rate?.toFixed(2) || '0.0'}x
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-600 dark:text-slate-400 mb-1">Customer LTV</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(currentMerchant.ltv || 0)}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-600 dark:text-slate-400 mb-1">Email Subscribers</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(currentMerchant.email_subscriber_count || 0)}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-600 dark:text-slate-400 mb-1">Acquisition Cost</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(currentMerchant.customer_acquisition_cost || 0)}
                    </p>
                </div>
                </div>
            </Card>
        </div>

      </div>
    </div>
  )
}

export default Dashboard