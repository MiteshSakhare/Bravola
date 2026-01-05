import React from 'react'
import clsx from 'clsx'

const Card = ({ title, subtitle, children, className = '', actions = null }) => {
  return (
    <div className={clsx('card', className)}>
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          </div>
          {actions && <div>{actions}</div>}
        </div>
      )}
      {children}
    </div>
  )
}

export default Card
