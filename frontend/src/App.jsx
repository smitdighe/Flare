import { Routes, Route } from 'react-router-dom';
import { AnimatePresence, motion } from 'motion/react';
import FlareLanding from './components/FlareLanding.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import './styles/tokens.css';
import './styles/app.css';
import './styles/landing.css';
import './styles/dashboard.css';

export default function App() {
  return (
    <AnimatePresence mode="wait" initial={false}>
      <Routes>
        <Route path="/" element={
          <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 0.985 }} transition={{ duration: 0.35 }}>
            <FlareLanding onLaunch={() => window.location.href = '/login'} />
          </motion.div>
        } />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <motion.div key="dashboard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.35 }}>
              <DashboardPage />
            </motion.div>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <motion.div key="settings" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.35 }}>
              <SettingsPage onBack={() => window.history.back()} />
            </motion.div>
          </ProtectedRoute>
        } />
        <Route path="*" element={
          <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0a1a', color: '#666' }}>
            <div style={{ textAlign: 'center' }}>
              <h1 style={{ color: '#e94560', fontSize: 48 }}>404</h1>
              <p>Page not found</p>
              <a href="/" style={{ color: '#e94560' }}>Go home</a>
            </div>
          </div>
        } />
      </Routes>
    </AnimatePresence>
  );
}
