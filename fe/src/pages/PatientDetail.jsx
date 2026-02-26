import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Avatar from '../components/Avatar';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import Modal from '../components/Modal';
import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import Table from '../components/Table';
import { patientService } from '../services/api';
import { useToast } from '../hooks';
import { formatDate } from '../utils/helpers';

const PatientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error: showError } = useToast();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [imageUploadModal, setImageUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);

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
  }, [id, navigate, showError]);

  const handleImageUpload = async (file) => {
    setUploading(true);
    try {
      await patientService.uploadImage(id, file);
      success('Image uploaded successfully');
      setImageUploadModal(false);
      // Refresh patient data
      const response = await patientService.getById(id);
      setPatient(response.data);
    } catch (error) {
      showError('Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

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
    { key: 'name', label: 'Treatment' },
    { key: 'status', label: 'Status', render: (status) => (
      <Badge variant={status === 'completed' ? 'success' : 'info'}>{status}</Badge>
    )},
    { key: 'date', label: 'Date', render: (date) => formatDate(date) },
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

        {/* Images */}
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Medical Images</h3>
              <Button size="sm" onClick={() => setImageUploadModal(true)}>
                + Upload Image
              </Button>
            </div>
          </Card.Header>
          <Card.Body>
            {patient.images && patient.images.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {patient.images.map((img) => (
                  <img
                    key={img.id}
                    src={img.image}
                    alt="Patient"
                    className="rounded-lg object-cover h-40 w-full"
                  />
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">No images uploaded</p>
            )}
          </Card.Body>
        </Card>
      </div>

      {/* Image Upload Modal */}
      <Modal
        isOpen={imageUploadModal}
        onClose={() => setImageUploadModal(false)}
        title="Upload Medical Image"
        footer={
          <>
            <Button variant="secondary" onClick={() => setImageUploadModal(false)}>
              Cancel
            </Button>
            <Button loading={uploading}>Upload</Button>
          </>
        }
      >
        <FileUpload
          label="Select image to upload"
          onUpload={handleImageUpload}
          accept="image/*"
          helperText="Max file size: 5MB"
        />
      </Modal>
    </MainLayout>
  );
};

export default PatientDetail;
