import React from 'react'
import { Heart } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-500 fill-current" />
            <span>by Bravola Team</span>
          </div>
          <div className="flex space-x-6 text-sm text-gray-600">
            <a href="#" className="hover:text-primary-600">
              Documentation
            </a>
            <a href="#" className="hover:text-primary-600">
              Support
            </a>
            <a href="#" className="hover:text-primary-600">
              Privacy Policy
            </a>
          </div>
        </div>
        <div className="mt-4 text-center text-xs text-gray-500">
          © 2025 Bravola Mini SaaS. All rights reserved.
        </div>
      </div>
    </footer>
  )
}

export default Footer
