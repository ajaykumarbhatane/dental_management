import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Avatar from '../components/Avatar';
import LoadingSpinner from '../components/LoadingSpinner';
import Table from '../components/Table';
import Modal from '../components/Modal';
import Input from '../components/Input';
import Select from '../components/Select';
import Textarea from '../components/Textarea';
import { patientService } from '../services/api';
import { useToast } from '../hooks';
import { useForm } from 'react-hook-form';
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
  const [selectedTreatment, setSelectedTreatment] = useState(null);
  const [treatmentDetailOpen, setTreatmentDetailOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      contact_number: '',
      secondary_contact_number: '',
      address: '',
      gender: '',
      date_of_birth: '',
      clinical_history: '',
      notes: '',
    },
  });

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await patientService.getById(id);
        setPatient(response.data);
        // populate form for edit
        reset({
          first_name: response.data.first_name || '',
          last_name: response.data.last_name || '',
          email: response.data.email || '',
          contact_number: response.data.contact_number || '',
          secondary_contact_number: response.data.secondary_contact_number || '',
          address: response.data.address || '',
          gender: response.data.gender || '',
          date_of_birth: response.data.date_of_birth || '',
          clinical_history: response.data.clinical_history || '',
          notes: response.data.notes || '',
        });
      } catch (error) {
        showError('Failed to load patient');
        navigate('/patients');
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [id, reset]);

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
    { 
      key: 'visit_number',
      label: 'Visit Number',
      render: (_, treatment, index) => (
        <span className="font-semibold text-primary-600">{index + 1}</span>
      )
    },
    { key: 'treatment_type', label: 'Treatment' },
    { 
      key: 'status', 
      label: 'Status', 
      render: (status) => (
        <Badge variant={status === 'COMPLETED' ? 'success' : 'info'}>{status}</Badge>
      )
    },
    {
      key: 'visited',
      label: 'Visited',
      render: (_, treatment) => {
        const isVisited = treatment.status === 'COMPLETED' || (treatment.created_at && new Date(treatment.created_at) < new Date());
        return <span className={isVisited ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>{isVisited ? 'True' : 'False'}</span>;
      }
    },
    { 
      key: 'created_at', 
      label: 'Visited Date', 
      render: (date) => formatDate(date) 
    },
    { 
      key: 'next_visit_date', 
      label: 'Next Visit Date', 
      render: (date) => date ? formatDate(date) : '-' 
    },
  ];

  const handleEdit = async (data) => {
    setLoading(true);
    try {
      const payload = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email || null,
        contact_number: data.contact_number || null,
        secondary_contact_number: data.secondary_contact_number || null,
        address: data.address || null,
        gender: data.gender || null,
        date_of_birth: data.date_of_birth || null,
        clinical_history: data.clinical_history || null,
        notes: data.notes || null,
      };
      await patientService.update(id, payload);
      success('Patient updated successfully');
      setEditModalOpen(false);
      // refresh patient
      const response = await patientService.getById(id);
      setPatient(response.data);
    } catch (err) {
      showError('Failed to update patient');
    } finally {
      setLoading(false);
    }
  };

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
          <div className="flex items-center gap-4">
            <Button onClick={() => setEditModalOpen(true)}>Edit</Button>
            <Avatar name={`${patient.first_name} ${patient.last_name}`} size="lg" />
          </div>
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
                <p className="font-medium">{patient.email || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Contact Number</p>
                <p className="font-medium">{patient.contact_number || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Secondary Contact</p>
                <p className="font-medium">{patient.secondary_contact_number || 'Not provided'}</p>
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
              <h3 className="font-semibold text-gray-900">Medical Info</h3>
            </Card.Header>
            <Card.Body className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Clinical History</p>
                <p className="font-medium text-sm">{patient.clinical_history || 'None reported'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Additional Notes</p>
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
              onRowClick={(treatment) => {
                setSelectedTreatment(treatment);
                setTreatmentDetailOpen(true);
              }}
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
                  .map((treatment, index) => (
                    <div 
                      key={treatment.id} 
                      className="rounded-lg overflow-hidden border border-gray-200 cursor-pointer hover:shadow-lg transition-shadow"
                      onClick={() => {
                        setSelectedTreatment(treatment);
                        setTreatmentDetailOpen(true);
                      }}
                    >
                      <img
                        src={getImageUrl(treatment.upload_image)}
                        alt={`${treatment.treatment_type} treatment`}
                        className="object-cover h-40 w-full"
                      />
                      <div className="p-2 bg-gray-50 text-xs text-gray-600 space-y-1">
                        <p className="font-medium text-red-600">Visit Number: {index + 1}</p>
                        <p className="font-medium">{treatment.treatment_type}</p>
                        <p>Visited Date: {formatDate(treatment.created_at)}</p>
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

      {/* Treatment Detail Modal */}
      <Modal
        isOpen={treatmentDetailOpen}
        onClose={() => {
          setTreatmentDetailOpen(false);
          setSelectedTreatment(null);
        }}
        title="Treatment Details"
        size="lg"
        footer={
          <Button
            variant="secondary"
            onClick={() => {
              setTreatmentDetailOpen(false);
              setSelectedTreatment(null);
            }}
          >
            Close
          </Button>
        }
      >
        {selectedTreatment && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Treatment Type</p>
                <p className="font-semibold text-lg">{selectedTreatment.treatment_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant={selectedTreatment.status === 'COMPLETED' ? 'success' : 'info'} className="mt-1">
                  {selectedTreatment.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Visited Date</p>
                <p className="font-medium">{formatDate(selectedTreatment.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Next Visit Date</p>
                <p className="font-medium">{selectedTreatment.next_visit_date ? formatDate(selectedTreatment.next_visit_date) : '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Doctor</p>
                <p className="font-medium">{selectedTreatment.doctor_name || 'Not assigned'}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Treatment Information</p>
              <p className="font-medium text-gray-900 bg-gray-50 p-3 rounded-lg">
                {selectedTreatment.treatment_information}
              </p>
            </div>

            {selectedTreatment.treatment_findings && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Clinical Findings</p>
                <p className="font-medium text-gray-900 bg-gray-50 p-3 rounded-lg">
                  {selectedTreatment.treatment_findings}
                </p>
              </div>
            )}

            {selectedTreatment.upload_image && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Treatment Image</p>
                <img 
                  src={getImageUrl(selectedTreatment.upload_image)}
                  alt="Treatment" 
                  className="rounded-lg max-h-96 w-full object-cover border border-gray-200"
                />
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Edit Patient Modal */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Patient"
        size="lg"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setEditModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSubmit(handleEdit)}>Save Changes</Button>
          </>
        }
      >
        <form className="space-y-4 max-h-96 overflow-y-auto">
          {/* Basic Information */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Basic Information</h3>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="First Name *"
                placeholder="Enter First Name"
                {...register('first_name', { required: 'First name is required' })}
                error={errors.first_name?.message}
                container="mb-0"
              />
              <Input
                label="Last Name *"
                placeholder="Enter Last Name"
                {...register('last_name', { required: 'Last name is required' })}
                error={errors.last_name?.message}
                container="mb-0"
              />
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Contact Information</h3>
            <div className="space-y-3">
              <Input
                label="Email"
                placeholder="Enter email address"
                type="email"
                {...register('email')}
                error={errors.email?.message}
                container="mb-0"
              />
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Contact Number"
                  placeholder="+91 12345 67890"
                  {...register('contact_number')}
                  error={errors.contact_number?.message}
                  container="mb-0"
                />
                <Input
                  label="Secondary Contact"
                  placeholder="+91 12345 67891"
                  {...register('secondary_contact_number')}
                  error={errors.secondary_contact_number?.message}
                  container="mb-0"
                />
              </div>
              <Textarea
                label="Address"
                placeholder="Enter patient address"
                {...register('address')}
                error={errors.address?.message}
                container="mb-0"
                rows="2"
              />
            </div>
          </div>

          {/* Personal Information */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Personal Information</h3>
            <div className="grid grid-cols-2 gap-3">
              <Select
                label="Gender"
                {...register('gender')}
                error={errors.gender?.message}
                container="mb-0"
              >
                <option value="">Select Gender</option>
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </Select>
              <Input
                label="Date of Birth"
                type="date"
                {...register('date_of_birth')}
                error={errors.date_of_birth?.message}
                container="mb-0"
              />
            </div>
          </div>

          {/* Medical Information */}
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Medical Information</h3>
            <div className="space-y-3">
              <Textarea
                label="Clinical History"
                placeholder="Enter clinical history and notes"
                {...register('clinical_history')}
                error={errors.clinical_history?.message}
                container="mb-0"
                rows="2"
              />
              <Textarea
                label="Additional Notes"
                placeholder="Any additional notes about the patient"
                {...register('notes')}
                error={errors.notes?.message}
                container="mb-0"
                rows="2"
              />
            </div>
          </div>
        </form>
      </Modal>
    </MainLayout>
  );
};

export default PatientDetail;
