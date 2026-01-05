import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

// Pages
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Discovery from './pages/Discovery'
import Benchmark from './pages/Benchmark'
import Strategy from './pages/Strategy'
import Campaigns from './pages/Campaigns'
import Settings from './pages/Settings'

// Components
import Layout from './components/layout/Layout'
import ErrorBoundary from './components/common/ErrorBoundary'

function App() {
  const { isAuthenticated } = useSelector((state) => state.auth)

  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/discovery" element={<Discovery />} />
                  <Route path="/benchmark" element={<Benchmark />} />
                  <Route path="/strategy" element={<Strategy />} />
                  <Route path="/campaigns" element={<Campaigns />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
