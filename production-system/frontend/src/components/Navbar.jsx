import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
// Mock analytics to avoid circular dependency
const analytics = {
  trackLogout: () => {},
  trackMenuClick: () => {}
};

const Navbar = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    analytics.trackLogout();
    onLogout();
  };

  const handleMenuClick = (item) => {
    analytics.trackMenuClick(item);
    setIsOpen(false);
  };

  const navItems = [
    { path: '/dashboard', label: 'DASHBOARD' },
    { path: '/analysis', label: 'ANALYSIS' },
    { path: '/cvs', label: 'CV_LIBRARY' },
    { path: '/job-descriptions', label: 'JOB_SPECS' },
    { path: '/comparisons', label: 'RESULTS' },
    { path: '/profile', label: 'PROFILE' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link
          to="/dashboard"
          className="navbar-brand"
          onClick={() => handleMenuClick('logo')}
        >
          CV_ANALYZER.SYS
        </Link>

        {/* Desktop Navigation */}
        <ul className="navbar-nav">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => handleMenuClick(item.label)}
              >
                {item.label}
              </Link>
            </li>
          ))}
          <li className="nav-item">
            <button
              onClick={handleLogout}
              className="nav-link"
              style={{
                background: 'none',
                border: 'none',
                padding: '12px 16px',
                margin: 0,
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}
            >
              LOGOUT
            </button>
          </li>
        </ul>

        {/* Mobile menu button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="btn"
          style={{ display: 'none' }}
        >
          [MENU]
        </button>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div style={{
          backgroundColor: '#1a1a1a',
          borderTop: '1px solid #333333',
          padding: '12px 0'
        }}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => handleMenuClick(item.label)}
              style={{ display: 'block', padding: '8px 20px' }}
            >
              {item.label}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="nav-link"
            style={{
              background: 'none',
              border: 'none',
              padding: '8px 20px',
              width: '100%',
              textAlign: 'left',
              cursor: 'pointer'
            }}
          >
            LOGOUT
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;