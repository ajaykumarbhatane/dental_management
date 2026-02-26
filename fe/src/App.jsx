import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import ProtectedRoute from './utils/ProtectedRoute';
import useAuth from './hooks/useAuth';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import PatientDetail from './pages/PatientDetail';
import Treatments from './pages/Treatments';
import Appointments from './pages/Appointments';
import Settings from './pages/Settings';
import Profile from './pages/Profile';

// Layouts
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const { isInitialized } = useAuth();

  if (!isInitialized) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Router>
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute><Dashboard /></ProtectedRoute>
          } />

          <Route path="/patients" element={
            <ProtectedRoute><Patients /></ProtectedRoute>
          } />

          <Route path="/patients/:id" element={
            <ProtectedRoute><PatientDetail /></ProtectedRoute>
          } />

          <Route path="/treatments" element={
            <ProtectedRoute><Treatments /></ProtectedRoute>
          } />

          <Route path="/appointments" element={
            <ProtectedRoute><Appointments /></ProtectedRoute>
          } />

          <Route path="/settings" element={
            <ProtectedRoute><Settings /></ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute><Profile /></ProtectedRoute>
          } />

          {/* Fallback */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>

      {/* Toast Notifications */}
      <Toaster position="top-right" />
    </>
  );
}

export default App;
