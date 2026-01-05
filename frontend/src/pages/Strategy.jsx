import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { generateStrategies, fetchStrategies, implementStrategy } from '@/store/slices/strategySlice'
import Card from '@/components/common/Card'
import Button from '@/components/common/Button'
import Loading from '@/components/common/Loading'
import Modal from '@/components/common/Modal'
import StrategyList from '@/components/strategy/StrategyList'
import { Sparkles } from 'lucide-react'

const Strategy = () => {
  const dispatch = useDispatch()
  const { items: strategies = [], loading } = useSelector((state) => state.strategy || { items: [] })
  
  const [selectedStrategy, setSelectedStrategy] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    dispatch(fetchStrategies())
  }, [dispatch])

  const handleGenerate = async () => {
    await dispatch(generateStrategies(5))
  }

  const handleSelectStrategy = (strategy) => {
    setSelectedStrategy(strategy)
    setShowModal(true)
  }

  const handleImplement = async () => {
    if (!selectedStrategy) return;
    // ✅ FIX: Dispatch the implementation action
    await dispatch(implementStrategy(selectedStrategy.id));
    setShowModal(false);
    // Refresh to show updated status
    dispatch(fetchStrategies());
  }

  if (loading && strategies.length === 0) return <Loading text="Loading strategies..." />

  return (
    <div className="space-y-8 animate-slide-in">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">AI Strategy Engine</h1>
        <Button onClick={handleGenerate} icon={Sparkles}>Generate New</Button>
      </div>

      <StrategyList 
        strategies={strategies} 
        onSelect={handleSelectStrategy} 
      />

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={selectedStrategy?.strategy_name}
      >
        <div className="space-y-6">
          <p className="text-gray-600">{selectedStrategy?.description}</p>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Expected Impact</h4>
            <div className="flex gap-4">
              <div>
                <span className="text-sm text-gray-500">ROI</span>
                <p className="font-bold text-green-600">{selectedStrategy?.expected_roi}%</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Effort</span>
                <p className="font-bold capitalize">{selectedStrategy?.estimated_effort}</p>
              </div>
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <Button 
              className="flex-1" 
              onClick={handleImplement}
              disabled={selectedStrategy?.status === 'active'}
            >
              {selectedStrategy?.status === 'active' ? 'Active' : 'Implement Strategy'}
            </Button>
            <Button variant="outline" onClick={() => setShowModal(false)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default Strategy