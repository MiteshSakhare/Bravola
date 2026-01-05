import React from 'react'
import clsx from 'clsx'

const Input = ({
  label,
  error,
  helpText,
  className = '',
  ...props
}) => {
  return (
    <div className={clsx('space-y-1', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        className={clsx(
          'input',
          error && 'border-red-500 focus:ring-red-500'
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helpText && (
        <p className="text-sm text-gray-500">{helpText}</p>
      )}
    </div>
  )
}

export default Input
