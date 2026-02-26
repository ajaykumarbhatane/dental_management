import React, { useState, useEffect } from 'react';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Input from '../components/Input';
import Select from '../components/Select';
import Modal from '../components/Modal';
import FileUpload from '../components/FileUpload';
import Table from '../components/Table';
import Textarea from '../components/Textarea';
import LoadingSpinner from '../components/LoadingSpinner';
import { treatmentService, patientService } from '../services/api';
import { useToast } from '../hooks';
import { useForm } from 'react-hook-form';
import { formatDate, getTreatmentStatus } from '../utils/helpers';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Helper to construct full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  // Remove /api from base URL to get server URL
  const serverBase = API_BASE_URL.replace('/api', '');
  return `${serverBase}${imageUrl}`;
};

const Treatments = () => {
  const { success, error: showError } = useToast();
  const [treatments, setTreatments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [selectedTreatment, setSelectedTreatment] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      patient: '',
      treatment_type: '',
      status: 'SCHEDULED',
      next_visit_date: '',
      treatment_information: '',
    },
  });

  // Fetch treatments and patients
  useEffect(() => {
    const fetchTreatments = async () => {
      try {
        const params = {};
        if (searchQuery) params.search = searchQuery;
        if (filterStatus) params.status = filterStatus;

        const response = await treatmentService.getAll(params);
        setTreatments(response.data.results || response.data);
      } catch (error) {
        showError('Failed to load treatments');
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(() => {
      fetchTreatments();
    }, 300);

    return () => clearTimeout(debounce);
  }, [searchQuery, filterStatus]);

  // Fetch patients for dropdown
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await patientService.getAll();
        setPatients(response.data.results || response.data);
      } catch (error) {
        console.error('Failed to load patients:', error);
      }
    };

    if (addModalOpen) {
      fetchPatients();
    }
  }, [addModalOpen]);

  // Add new treatment
  const onSubmit = async (data) => {
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('patient', parseInt(data.patient, 10)); // Convert to integer
      formData.append('treatment_type', data.treatment_type);
      formData.append('status', data.status);
      formData.append('next_visit_date', data.next_visit_date);
      formData.append('treatment_information', data.treatment_information);
      
      // Only append image if one was actually selected
      if (imageFile) {
        formData.append('upload_image', imageFile);
      }

      await treatmentService.create(formData);

      success('Treatment recorded successfully');
      setAddModalOpen(false);
      reset();
      setImageFile(null);
      // Refresh list
      const response = await treatmentService.getAll();
      setTreatments(response.data.results || response.data);
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to add treatment');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    { key: 'patient_name', label: 'Patient' },
    { key: 'treatment_type', label: 'Type' },
    { 
      key: 'status', 
      label: 'Status',
      render: (status) => {
        const { color, label } = getTreatmentStatus(status);
        return <Badge variant={color}>{label}</Badge>;
      },
    },
    {
      key: 'created_at',
      label: 'Date',
      render: (value) => formatDate(value),
    },
  ];

  const statusOptions = [
    { value: 'SCHEDULED', label: 'Scheduled' },
    { value: 'ONGOING', label: 'Ongoing' },
    { value: 'COMPLETED', label: 'Completed' },
    { value: 'CANCELLED', label: 'Cancelled' },
    { value: 'ON_HOLD', label: 'On Hold' },
  ];

  const treatmentTypes = [
    { value: 'BRACES', label: 'Traditional Braces' },
    { value: 'ALIGNERS', label: 'Clear Aligners (Invisalign)' },
    { value: 'RETAINER', label: 'Retainer' },
    { value: 'EXTRACTION', label: 'Extraction' },
    { value: 'SCALING', label: 'Scaling & Root Planing' },
    { value: 'ORTHOGNATHIC', label: 'Orthognathic Surgery Planning' },
    { value: 'PROPHYLAXIS', label: 'Prophylaxis (Cleaning)' },
    { value: 'OTHER', label: 'Other' },
  ];

  return (
    <MainLayout>
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Treatments</h1>
            <p className="text-gray-600">Manage patient treatments and procedures</p>
          </div>
          <Button onClick={() => setAddModalOpen(true)}>+ Record Treatment</Button>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <Card.Body className="p-0">
              <Input
                placeholder="Search by patient name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                container="mb-0"
              />
            </Card.Body>
          </Card>

          <Card>
            <Card.Body className="p-0">
              <Select
                options={statusOptions}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                container="mb-0"
              />
            </Card.Body>
          </Card>
        </div>

        {/* Table */}
        <Card>
          <Card.Body>
            {loading ? (
              <LoadingSpinner size="md" fullHeight={false} />
            ) : (
              <Table 
                columns={columns} 
                data={treatments} 
                isResponsive={true}
                onRowClick={(treatment) => {
                  setSelectedTreatment(treatment);
                  setDetailModalOpen(true);
                }}
              />
            )}
          </Card.Body>
        </Card>
      </div>

      <Modal
        isOpen={addModalOpen}
        onClose={() => {
          setAddModalOpen(false);
          reset();
          setImageFile(null);
        }}
        title="Record New Treatment"
        size="lg"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                setAddModalOpen(false);
                reset();
                setImageFile(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleSubmit(onSubmit)} loading={submitting}>
              Save Treatment
            </Button>
          </>
        }
      >
        <form className="space-y-4">
          <Select
            label="Patient"
            options={patients.map(p => ({
              value: p.user_id,
              label: `${p.first_name} ${p.last_name}${p.email ? ` (${p.email})` : ''}`
            }))}
            {...register('patient', { required: 'Patient is required' })}
            error={errors.patient?.message}
            container="mb-0"
          />

          <Select
            label="Treatment Type"
            options={treatmentTypes}
            {...register('treatment_type', { required: 'Treatment type is required' })}
            error={errors.treatment_type?.message}
            container="mb-0"
          />

          <Input
            label="Next Visit Date"
            type="date"
            {...register('next_visit_date', { required: 'Date is required' })}
            error={errors.next_visit_date?.message}
            container="mb-0"
          />

          <Select
            label="Status"
            options={statusOptions}
            {...register('status')}
            error={errors.status?.message}
            container="mb-0"
          />

          <Textarea
            label="Treatment Information"
            {...register('treatment_information')}
            error={errors.treatment_information?.message}
            container="mb-0"
          />

          <FileUpload
            label="Upload Image (optional)"
            onUpload={(file) => setImageFile(file)}
            helperText="Max 5MB"
          />
        </form>
      </Modal>

      {/* Treatment Detail Modal */}
      <Modal
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setSelectedTreatment(null);
        }}
        title="Treatment Details"
        size="lg"
        footer={
          <Button
            variant="secondary"
            onClick={() => {
              setDetailModalOpen(false);
              setSelectedTreatment(null);
            }}
          >
            Close
          </Button>
        }
      >
        {selectedTreatment && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Patient</p>
                <p className="font-medium">{selectedTreatment.patient_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Type</p>
                <p className="font-medium">{selectedTreatment.treatment_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant={selectedTreatment.status === 'COMPLETED' ? 'success' : 'info'}>
                  {selectedTreatment.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date</p>
                <p className="font-medium">{formatDate(selectedTreatment.created_at)}</p>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-gray-600">Treatment Information</p>
              <p className="font-medium">{selectedTreatment.treatment_information}</p>
            </div>

            {selectedTreatment.treatment_findings && (
              <div>
                <p className="text-sm text-gray-600">Findings</p>
                <p className="font-medium">{selectedTreatment.treatment_findings}</p>
              </div>
            )}

            {selectedTreatment.upload_image && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Treatment Image</p>
                <img 
                  src={getImageUrl(selectedTreatment.upload_image)}
                  alt="Treatment" 
                  className="rounded-lg max-h-96 w-full object-cover"
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </MainLayout>
  );
};

export default Treatments;
