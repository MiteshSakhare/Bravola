import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchCampaigns } from '@/store/slices/campaignSlice' // Ensure this slice exists
import Card from '@/components/common/Card'
import Loading from '@/components/common/Loading'
import { Mail, TrendingUp, DollarSign, MousePointer } from 'lucide-react'

const Campaigns = () => {
  const dispatch = useDispatch()
  // Fetch from Redux store
  const { items: campaigns = [], loading } = useSelector((state) => state.campaigns || { items: [] })

  useEffect(() => {
    dispatch(fetchCampaigns())
  }, [dispatch])

  if (loading) return <Loading text="Loading campaigns..." />

  return (
    <div className="space-y-8 animate-slide-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Campaigns</h1>
        <p className="text-gray-600 mt-2">
          Track your campaign performance
        </p>
      </div>

      {campaigns.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Campaigns Found</h3>
            <p className="text-gray-600">Import data or connect Klaviyo to see results.</p>
          </div>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((camp) => (
            <Card key={camp.id || camp.campaign_id} title={camp.campaign_name}>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Type</span>
                  <span className="font-medium bg-blue-50 text-blue-700 px-2 py-1 rounded">{camp.campaign_type}</span>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <p className="text-xs text-gray-500">Revenue</p>
                    <p className="font-bold text-green-600 flex items-center">
                      <DollarSign className="w-3 h-3 mr-1" />
                      {camp.revenue?.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">ROI</p>
                    <p className="font-bold text-indigo-600">
                      {camp.roi ? `${camp.roi}x` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default Campaigns