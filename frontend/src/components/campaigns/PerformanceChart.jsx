import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const PerformanceChart = ({ data, title = 'Campaign Performance' }) => {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="open_rate"
            stroke="#0ea5e9"
            name="Open Rate"
          />
          <Line
            type="monotone"
            dataKey="click_rate"
            stroke="#10b981"
            name="Click Rate"
          />
          <Line
            type="monotone"
            dataKey="conversion_rate"
            stroke="#f59e0b"
            name="Conversion Rate"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PerformanceChart
