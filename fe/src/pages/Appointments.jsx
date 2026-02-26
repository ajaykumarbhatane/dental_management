import React from 'react';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';

const Appointments = () => {
  return (
    <MainLayout>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Appointments</h1>
        <p className="text-gray-600 mb-8">Schedule and manage appointments</p>

        <Card>
          <Card.Body>
            <div className="text-center py-12">
              <p className="text-gray-600">Coming soon...</p>
              <p className="text-sm text-gray-500 mt-2">Appointment scheduling feature is under development</p>
            </div>
          </Card.Body>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Appointments;
