import React, { useEffect, useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import useAuth from '../hooks/useAuth';
import api from '../services/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    total_patients: 0,
    total_treatments: 0,
    pending_appointments: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch real data from API
        const [patientsRes, treatmentsRes] = await Promise.all([
          api.get('/patients/'),
          api.get('/treatments/'),
        ]);

        // Get patient and treatment counts
        // API returns paginated results; use .count when available
        const totalPatients = (patientsRes.data && patientsRes.data.count !== undefined)
          ? patientsRes.data.count
          : (Array.isArray(patientsRes.data) ? patientsRes.data.length : (patientsRes.data.results || []).length);

        const treatmentsList = Array.isArray(treatmentsRes.data)
          ? treatmentsRes.data
          : treatmentsRes.data.results || [];

        // Count ongoing and scheduled
        const totalOngoing = treatmentsList.filter(t => t.status === 'ONGOING').length;
        const pendingTreatments = treatmentsList.filter(t => t.status === 'SCHEDULED').length;

        setStats({
          total_patients: totalPatients,
          total_treatments: totalOngoing,
          pending_appointments: pendingTreatments,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        // Fallback to empty stats on error
        setStats({
          total_patients: 0,
          total_treatments: 0,
          pending_appointments: 0,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <MainLayout>
      <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, Dr. {user?.first_name}! Here&apos;s your clinic overview.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <Card.Body>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Patients</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_patients}</p>
                </div>
                <div className="text-4xl">👥</div>
              </div>
            </Card.Body>
          </Card>

          <Card>
            <Card.Body>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Active Treatments</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_treatments}</p>
                </div>
                <div className="text-4xl">🏥</div>
              </div>
            </Card.Body>
          </Card>

          <Card>
            <Card.Body>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Pending Appointments</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.pending_appointments}</p>
                </div>
                <div className="text-4xl">📅</div>
              </div>
            </Card.Body>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </Card.Header>
            <Card.Body className="space-y-3">
              <Button className="w-full justify-center">+ Add New Patient</Button>
              <Button className="w-full justify-center" variant="secondary">+ Schedule Appointment</Button>
              <Button className="w-full justify-center" variant="secondary">+ Record Treatment</Button>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900">Today&apos;s Schedule</h3>
            </Card.Header>
            <Card.Body>
              <p className="text-gray-600 text-center py-8">No appointments scheduled for today</p>
            </Card.Body>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
