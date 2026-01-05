import React from 'react'
import { PERSONA_COLORS } from '@/utils/constants'
import { CheckCircle2 } from 'lucide-react'

const PersonaCard = ({ persona, confidence, characteristics = [] }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Your Persona</h3>
        <span className="text-sm text-gray-500">
          {(confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <div className="mb-6">
        <span
          className={`inline-block px-4 py-2 rounded-full text-lg font-medium ${
            PERSONA_COLORS[persona] || 'bg-gray-100 text-gray-800'
          }`}
        >
          {persona}
        </span>
      </div>

      {characteristics.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900">Key Characteristics</h4>
          <ul className="space-y-2">
            {characteristics.map((char, index) => (
              <li key={index} className="flex items-start space-x-2">
                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-gray-700">{char}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default PersonaCard
