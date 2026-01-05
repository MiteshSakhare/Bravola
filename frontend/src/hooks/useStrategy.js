import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { generateStrategies, fetchStrategies } from '@/store/slices/strategySlice'

export const useStrategy = () => {
  const dispatch = useDispatch()
  const { strategies, recommendations, loading, error } = useSelector(
    (state) => state.strategy
  )

  const generate = async (limit = 5) => {
    return await dispatch(generateStrategies(limit))
  }

  const fetchAll = async () => {
    return await dispatch(fetchStrategies())
  }

  useEffect(() => {
    if (strategies.length === 0 && !loading && !error) {
      fetchAll()
    }
  }, [strategies, loading, error])

  return {
    strategies,
    recommendations,
    loading,
    error,
    generate,
    fetchAll,
  }
}
