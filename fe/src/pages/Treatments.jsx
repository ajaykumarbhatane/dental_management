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

const Treatments = () => {
  const { success, error: showError } = useToast();
  const [treatments, setTreatments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

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
      // map form fields to API payload
      const payload = {
        patient: data.patient,
        treatment_type: data.treatment_type,
        status: data.status,
        next_visit_date: data.next_visit_date,
        treatment_information: data.treatment_information,
      };

      await treatmentService.create(payload);
      success('Treatment recorded successfully');
      setAddModalOpen(false);
      reset();
      // Refresh list
      const response = await treatmentService.getAll();
      setTreatments(response.data.results || response.data);
    } catch (error) {
      showError('Failed to add treatment');
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
              <Table columns={columns} data={treatments} isResponsive={true} />
            )}
          </Card.Body>
        </Card>
      </div>

      {/* Add Treatment Modal */}
      <Modal
        isOpen={addModalOpen}
        onClose={() => {
          setAddModalOpen(false);
          reset();
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
              value: p.id,
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
            onUpload={(file) => console.log('Image:', file)}
            helperText="Max 5MB"
          />
        </form>
      </Modal>
    </MainLayout>
  );
};

export default Treatments;
