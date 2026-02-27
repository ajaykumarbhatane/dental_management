import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import useUIStore from '../store/uiStore';
import Avatar from './Avatar';
import { cn } from '../utils/helpers';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { setSidebarOpen, toggleSidebar } = useUIStore();
  const [showProfile, setShowProfile] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="h-16 bg-white border-b border-gray-200 shadow-soft-md sticky top-0 z-40">
      <div className="h-full px-6 flex items-center justify-between">
        {/* Left section */}
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-smooth md:hidden"
            title="Toggle sidebar"
          >
            ☰
          </button>

          <div>
            <h2 className="text-sm text-gray-500">Welcome to,</h2>
            <p className="text-gray-900 font-semibold">{user?.clinic_name || 'Clinic'}</p>
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-6">
          {/* Search bar - hidden on mobile */}
          <div className="hidden sm:block relative">
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              🔍
            </span>
          </div>

          {/* Profile dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-smooth"
            >
              <Avatar
                name={`Dr.${user?.first_name || ''} ${user?.last_name || ''}`}
                size="sm"
              />
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-gray-900">
                  Dr. {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">{user?.role || 'User'}</p>
              </div>
            </button>

            {/* Dropdown menu */}
            {showProfile && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                <button
                  onClick={() => {
                    navigate('/profile');
                    setShowProfile(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-smooth"
                >
                  👤 Profile
                </button>
                <button
                  onClick={() => {
                    navigate('/settings');
                    setShowProfile(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-smooth"
                >
                  ⚙️ Clinic Settings
                </button>
                <hr className="my-2" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-smooth"
                >
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
