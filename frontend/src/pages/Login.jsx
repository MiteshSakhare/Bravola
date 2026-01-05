import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { login, register, clearError } from '@/store/slices/authSlice'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import { LogIn, UserPlus } from 'lucide-react'

const Login = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { isAuthenticated, loading, error } = useSelector((state) => state.auth)

  const [isRegisterMode, setIsRegisterMode] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    shop_name: '',
    shop_domain: '',
    vertical: 'Fashion',
  })

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    dispatch(clearError())
  }, [isRegisterMode, dispatch])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (isRegisterMode) {
      const result = await dispatch(register(formData))
      if (!result.error) {
        // Auto-login after registration
        await dispatch(login({ email: formData.email, password: formData.password }))
      }
    } else {
      await dispatch(login({ email: formData.email, password: formData.password }))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo & Title */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary-600 mb-2">Bravola</h1>
            <p className="text-gray-600">AI-Powered Growth Marketing Platform</p>
          </div>

          {/* Toggle Buttons */}
          <div className="flex space-x-2 mb-6 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setIsRegisterMode(false)}
              className={`flex-1 py-2 rounded-md transition-all ${
                !isRegisterMode
                  ? 'bg-white shadow-sm font-medium'
                  : 'text-gray-600'
              }`}
            >
              <LogIn className="w-4 h-4 inline mr-2" />
              Login
            </button>
            <button
              onClick={() => setIsRegisterMode(true)}
              className={`flex-1 py-2 rounded-md transition-all ${
                isRegisterMode
                  ? 'bg-white shadow-sm font-medium'
                  : 'text-gray-600'
              }`}
            >
              <UserPlus className="w-4 h-4 inline mr-2" />
              Register
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegisterMode && (
              <>
                <Input
                  label="Shop Name"
                  name="shop_name"
                  type="text"
                  placeholder="My Amazing Store"
                  value={formData.shop_name}
                  onChange={handleChange}
                  required
                />

                <Input
                  label="Shop Domain"
                  name="shop_domain"
                  type="text"
                  placeholder="mystore.myshopify.com"
                  value={formData.shop_domain}
                  onChange={handleChange}
                  required
                />

                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">
                    Vertical
                  </label>
                  <select
                    name="vertical"
                    value={formData.vertical}
                    onChange={handleChange}
                    className="input"
                    required
                  >
                    <option value="Fashion">Fashion</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Beauty">Beauty</option>
                    <option value="Home">Home</option>
                    <option value="Fitness">Fitness</option>
                    <option value="Food">Food</option>
                  </select>
                </div>
              </>
            )}

            <Input
              label="Email"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />

            <Input
              label="Password"
              name="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={loading}
              disabled={loading}
            >
              {isRegisterMode ? 'Create Account' : 'Sign In'}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center text-sm text-gray-600">
            {isRegisterMode ? (
              <p>
                Already have an account?{' '}
                <button
                  onClick={() => setIsRegisterMode(false)}
                  className="text-primary-600 hover:underline font-medium"
                >
                  Sign in
                </button>
              </p>
            ) : (
              <p>
                Don't have an account?{' '}
                <button
                  onClick={() => setIsRegisterMode(true)}
                  className="text-primary-600 hover:underline font-medium"
                >
                  Register now
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
