import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-blue-600">CreatorHub</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/marketplace" className="text-gray-700 hover:text-blue-600 transition-colors">
              Marketplace
            </Link>
            
            {user ? (
              <>
                <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
                {user.user_type === 'creator' && (
                  <Link to="/create-service" className="text-gray-700 hover:text-blue-600 transition-colors">
                    Create Service
                  </Link>
                )}
                <Link to="/profile" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Login
                </Link>
                <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-50">
            <Link to="/marketplace" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
              Marketplace
            </Link>
            
            {user ? (
              <>
                <Link to="/dashboard" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                  Dashboard
                </Link>
                {user.user_type === 'creator' && (
                  <Link to="/create-service" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                    Create Service
                  </Link>
                )}
                <Link to="/profile" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 text-red-600 hover:text-red-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="block px-3 py-2 text-gray-700 hover:text-blue-600">
                  Login
                </Link>
                <Link to="/register" className="block px-3 py-2 text-blue-600 hover:text-blue-700">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;