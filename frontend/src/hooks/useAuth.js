import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { login, register, logout } from '@/store/slices/authSlice'

export const useAuth = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user, isAuthenticated, loading, error } = useSelector((state) => state.auth)

  const handleLogin = async (credentials) => {
    const result = await dispatch(login(credentials))
    if (!result.error) {
      navigate('/')
    }
    return result
  }

  const handleRegister = async (userData) => {
    const result = await dispatch(register(userData))
    if (!result.error) {
      // Auto-login after registration
      await dispatch(login({ email: userData.email, password: userData.password }))
      navigate('/')
    }
    return result
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
  }
}
