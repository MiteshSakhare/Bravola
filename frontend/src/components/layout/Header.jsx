import React from 'react';
import { useAuth } from '../../hooks/useAuth';

const Header = ({ sidebarOpen, setSidebarOpen, darkMode, setDarkMode }) => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-10 flex w-full bg-white dark:bg-dark-card drop-shadow-sm dark:drop-shadow-none dark:border-b dark:border-dark-border">
      <div className="flex flex-grow items-center justify-between px-4 py-4 shadow-2 md:px-6 2xl:px-11">
        
        {/* Hamburger Menu (Mobile Only) */}
        <div className="flex items-center gap-2 sm:gap-4 lg:hidden">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSidebarOpen(!sidebarOpen);
            }}
            className="block rounded-sm border border-slate-200 bg-white p-1.5 shadow-sm dark:border-dark-border dark:bg-dark-card"
          >
            <span className="relative block h-5.5 w-5.5 cursor-pointer">
              <span className="du-block absolute right-0 h-full w-full">
                <span className="relative top-0 block my-1 h-0.5 w-0 rounded-sm bg-black delay-[0] duration-200 ease-in-out dark:bg-white" />
                <span className="relative top-0 block my-1 h-0.5 w-0 rounded-sm bg-black delay-150 duration-200 ease-in-out dark:bg-white" />
                <span className="relative top-0 block my-1 h-0.5 w-0 rounded-sm bg-black delay-200 duration-200 ease-in-out dark:bg-white" />
              </span>
            </span>
          </button>
        </div>

        {/* Right Side Tools */}
        <div className="flex items-center gap-3 2xsm:gap-7 ml-auto">
          
          {/* 🌙 Theme Toggler */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 text-slate-500 hover:bg-slate-100 dark:text-dark-muted dark:hover:bg-slate-800 rounded-full transition-colors"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>

          {/* User Profile */}
          <div className="flex items-center gap-4">
            <span className="hidden text-right lg:block">
              <span className="block text-sm font-medium text-black dark:text-white">
                {user?.shop_name || 'Merchant'}
              </span>
              <span className="block text-xs text-slate-500 dark:text-dark-muted">
                {user?.email}
              </span>
            </span>
            <button 
              onClick={logout}
              className="text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;