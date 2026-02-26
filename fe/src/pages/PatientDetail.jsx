import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Avatar from '../components/Avatar';
import LoadingSpinner from '../components/LoadingSpinner';
import Table from '../components/Table';
import { patientService } from '../services/api';
import { useToast } from '../hooks';
import { formatDate } from '../utils/helpers';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Helper to construct full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  const serverBase = API_BASE_URL.replace('/api', '');
  return `${serverBase}${imageUrl}`;
};

const PatientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error: showError } = useToast();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await patientService.getById(id);
        setPatient(response.data);
      } catch (error) {
        showError('Failed to load patient');
        navigate('/patients');
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [id]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!patient) {
    return (
      <MainLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Patient not found</p>
          <Button onClick={() => navigate('/patients')} className="mt-4">
            Back to Patients
          </Button>
        </div>
      </MainLayout>
    );
  }

  const treatmentColumns = [
    { key: 'treatment_type', label: 'Treatment' },
    { key: 'status', label: 'Status', render: (status) => (
      <Badge variant={status === 'COMPLETED' ? 'success' : 'info'}>{status}</Badge>
    )},
    { key: 'created_at', label: 'Date', render: (date) => formatDate(date) },
  ];

  return (
    <MainLayout>
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button onClick={() => navigate('/patients')} variant="ghost">← Back</Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{patient.first_name} {patient.last_name}</h1>
              <p className="text-gray-600">{patient.email}</p>
            </div>
          </div>
          <Avatar name={`${patient.first_name} ${patient.last_name}`} size="lg" />
        </div>

        {/* Tabs */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Basic Info */}
          <Card>
            <Card.Header>
              <h3 className="font-semibold text-gray-900">Basic Information</h3>
            </Card.Header>
            <Card.Body className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="font-medium">{patient.first_name} {patient.last_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date of Birth</p>
                <p className="font-medium">{formatDate(patient.date_of_birth)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Gender</p>
                <p className="font-medium capitalize">{patient.gender || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant="success" className="mt-1">Active</Badge>
              </div>
            </Card.Body>
          </Card>

          {/* Contact Info */}
          <Card>
            <Card.Header>
              <h3 className="font-semibold text-gray-900">Contact Information</h3>
            </Card.Header>
            <Card.Body className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{patient.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{patient.phone || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Address</p>
                <p className="font-medium text-sm">{patient.address || 'Not provided'}</p>
              </div>
            </Card.Body>
          </Card>

          {/* Medical History */}
          <Card>
            <Card.Header>
              <h3 className="font-semibold text-gray-900">Medical History</h3>
            </Card.Header>
            <Card.Body className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Allergies</p>
                <p className="font-medium">{patient.allergies || 'None reported'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Medications</p>
                <p className="font-medium text-sm">{patient.current_medications || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Notes</p>
                <p className="font-medium text-sm">{patient.notes || 'No notes'}</p>
              </div>
            </Card.Body>
          </Card>
        </div>

        {/* Treatment History */}
        <Card className="mb-8">
          <Card.Header>
            <h3 className="font-semibold text-gray-900">Treatment History</h3>
          </Card.Header>
          <Card.Body>
            <Table
              columns={treatmentColumns}
              data={patient.treatments || []}
              isResponsive={true}
            />
          </Card.Body>
        </Card>

        {/* Images from Treatments */}
        <Card>
          <Card.Header>
            <h3 className="font-semibold text-gray-900">Treatment Images</h3>
          </Card.Header>
          <Card.Body>
            {patient.treatments && patient.treatments.some(t => t.upload_image) ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {patient.treatments
                  .filter(t => t.upload_image)
                  .map((treatment) => (
                    <div key={treatment.id} className="rounded-lg overflow-hidden border border-gray-200">
                      <img
                        src={getImageUrl(treatment.upload_image)}
                        alt={`${treatment.treatment_type} treatment`}
                        className="object-cover h-40 w-full"
                      />
                      <div className="p-2 bg-gray-50 text-xs text-gray-600">
                        <p className="font-medium">{treatment.treatment_type}</p>
                        <p>{formatDate(treatment.created_at)}</p>
                      </div>
                    </div>
                  ))
                }
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">No treatment images uploaded</p>
            )}
          </Card.Body>
        </Card>
      </div>
    </MainLayout>
  );
};

export default PatientDetail;
