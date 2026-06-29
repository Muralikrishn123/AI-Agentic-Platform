import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useState, useEffect } from 'react';
import axios from 'axios';

const coreNav = [
  { to: '/dashboard', icon: '\u26a1', label: 'Dashboard' },
  { to: '/workflows',  icon: '\ud83d\udd04', label: 'Workflows' },
  { to: '/plugins',    icon: '🧩', label: 'Plugins' },
  { to: '/approvals',  icon: '✋', label: 'Approvals', badge: true },
  { to: '/logs',       icon: '\ud83d\udccb', label: 'Logs' },
  { to: '/reports',    icon: '\ud83d\udcca', label: 'Reports' },
];

const settingsNav = [
  { to: '/config', icon: '⚙️', label: 'ICP & Config' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    if (!user) return;  // Don't poll until authenticated
    const fetchPending = () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      axios.get('/api/hitl/pending', {
        headers: { Authorization: `Bearer ${token}` },
      }).then(r => setPendingCount(r.data.length)).catch(() => {});
    };
    fetchPending();
    const interval = setInterval(fetchPending, 15000);
    return () => clearInterval(interval);
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    : '??';

  return (
    <div className="app-layout">
      {/* Background Ambient Glows */}
      <div className="ambient-glow-1" />
      <div className="ambient-glow-2" />

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🤖</div>
          <div>
            <div className="sidebar-logo-text">Agentic AI</div>
            <div className="sidebar-logo-sub">Platform v3.0</div>
          </div>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          <div className="sidebar-section-label">Platform</div>
          {coreNav.map(({ to, icon, label, badge }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-item-icon">{icon}</span>
              {label}
              {badge && pendingCount > 0 && (
                <span style={{
                  marginLeft: 'auto', fontSize: 10, fontWeight: 700,
                  background: 'rgba(251,191,36,0.25)', color: '#fbbf24',
                  padding: '1px 7px', borderRadius: 10,
                  border: '1px solid rgba(251,191,36,0.4)',
                }}>
                  {pendingCount}
                </span>
              )}
            </NavLink>
          ))}

          <div className="sidebar-section-label" style={{ marginTop: 16 }}>Settings</div>
          {settingsNav.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-item-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer / user */}
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">{initials}</div>
            <div className="sidebar-user-name">{user?.name || 'User'}</div>
            <button
              className="sidebar-logout-btn"
              onClick={handleLogout}
              title="Logout"
            >
              ↩
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="main-content" style={{ position: 'relative', zIndex: 1 }}>
        <Outlet />
      </main>
    </div>
  );
}

