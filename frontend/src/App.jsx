import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import Plugins from './pages/Plugins';
import Logs from './pages/Logs';
import Reports from './pages/Reports';
import Approvals from './pages/Approvals';
import Config from './pages/Config';
import Results from './pages/Results';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="workflows" element={<Workflows />} />
            <Route path="plugins" element={<Plugins />} />
            <Route path="logs" element={<Logs />} />
            <Route path="reports" element={<Reports />} />
            <Route path="approvals" element={<Approvals />} />
            <Route path="config" element={<Config />} />
            <Route path="results/:workflowId" element={<Results />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
