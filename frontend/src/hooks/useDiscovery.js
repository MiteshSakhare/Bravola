import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { analyzeDiscovery, fetchDiscoveryProfile } from '@/store/slices/discoverySlice'

export const useDiscovery = () => {
  const dispatch = useDispatch()
  const { profile, analysis, loading, error } = useSelector((state) => state.discovery)

  const runAnalysis = async (forceRefresh = false) => {
    return await dispatch(analyzeDiscovery(forceRefresh))
  }

  const getProfile = async () => {
    return await dispatch(fetchDiscoveryProfile())
  }

  useEffect(() => {
    if (!profile && !loading && !error) {
      getProfile()
    }
  }, [profile, loading, error])

  return {
    profile,
    analysis,
    loading,
    error,
    runAnalysis,
    getProfile,
  }
}
