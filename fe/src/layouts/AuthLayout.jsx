import React from 'react';

const AuthLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white">Dental Pro</h1>
          <p className="text-primary-200 mt-2">Clinic Management System</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-primary-100">
          <p className="text-sm">© 2026 Dental Pro. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
