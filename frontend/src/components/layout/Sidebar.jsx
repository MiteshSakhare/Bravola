import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  BarChart3, // Benchmark
  Target,    // Strategy
  Mail,      // Campaigns
  Settings,
  X
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/discovery', label: 'Discovery', icon: Search },
  { path: '/benchmark', label: 'Benchmark', icon: BarChart3 },
  { path: '/strategy', label: 'Strategy', icon: Target },
  { path: '/campaigns', label: 'Campaigns', icon: Mail },
  { path: '/settings', label: 'Settings', icon: Settings },
]

const Sidebar = ({ isOpen, setIsOpen }) => {
  return (
    <aside 
      className={`
        absolute left-0 top-0 z-9999 flex h-screen w-72 flex-col overflow-y-hidden bg-white duration-300 ease-linear dark:bg-dark-card lg:static lg:translate-x-0 border-r border-slate-200 dark:border-dark-border
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between gap-2 px-6 py-5.5 lg:py-6.5">
        <div className="flex items-center gap-2 font-display font-bold text-2xl text-primary-600">
           <span>🚀</span> Bravola
        </div>

        <button
          onClick={() => setIsOpen(false)}
          className="block lg:hidden text-slate-500"
        >
          <X className="h-6 w-6" />
        </button>
      </div>

      {/* Nav Menu */}
      <div className="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
        <nav className="mt-5 py-4 px-4 lg:mt-9 lg:px-6">
          <ul className="mb-6 flex flex-col gap-1.5">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `group relative flex items-center gap-2.5 rounded-lg px-4 py-2 font-medium duration-300 ease-in-out ${
                        isActive
                          ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                          : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800'
                      }`
                    }
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar