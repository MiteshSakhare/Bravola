import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { analyzeBenchmark } from '@/store/slices/benchmarkSlice'

export const useBenchmark = () => {
  const dispatch = useDispatch()
  const { scores, analysis, loading, error } = useSelector((state) => state.benchmark)

  const runAnalysis = async (forceRefresh = false) => {
    return await dispatch(analyzeBenchmark(forceRefresh))
  }

  useEffect(() => {
    if (!scores && !loading && !error) {
      runAnalysis()
    }
  }, [scores, loading, error])

  return {
    scores,
    analysis,
    loading,
    error,
    runAnalysis,
  }
}
