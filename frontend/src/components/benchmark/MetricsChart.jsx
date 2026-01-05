import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const MetricsChart = ({ data, title }) => {
  return (
    <div>
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="your_value" fill="#0ea5e9" name="Your Value" />
          <Bar dataKey="peer_average" fill="#94a3b8" name="Peer Average" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default MetricsChart
