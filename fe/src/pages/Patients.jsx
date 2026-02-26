import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import Table from '../components/Table';
import Textarea from '../components/Textarea';
import LoadingSpinner from '../components/LoadingSpinner';
import { patientService } from '../services/api';
import api from '../services/api';
import useAuth from '../hooks/useAuth';
import { useToast } from '../hooks';
import { useForm } from 'react-hook-form';
import { validateEmail, formatDate } from '../utils/helpers';

const Patients = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { success, error: showError } = useToast();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      date_of_birth: '',
    },
  });

  // Fetch patients
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await patientService.getAll({ search: searchQuery });
        setPatients(response.data.results || response.data);
      } catch (error) {
        showError('Failed to load patients');
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(() => {
      fetchPatients();
    }, 300);

    return () => clearTimeout(debounce);
  }, [searchQuery]);

  // Add new patient (register via auth)
  const onSubmit = async (data) => {
    setSubmitting(true);
    try {
      // prepare registration payload
      const payload = {
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
        contact_number: data.phone,
        password: 'Patient123!',
        password_confirm: 'Patient123!',
        clinic_id: user?.clinic,
        role: 'PATIENT',
      };

      await api.post('/auth/register/', payload);
      success('Patient registered successfully');
      setAddModalOpen(false);
      reset();
      // Refresh list
      const response = await patientService.getAll({ search: searchQuery });
      setPatients(response.data.results || response.data);
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to add patient');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      key: 'user_full_name',
      label: 'Name',
      render: (value, row) => `${row.first_name || value} ${row.last_name || ''}`.trim(),
    },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    {
      key: 'date_of_birth',
      label: 'Date of Birth',
      render: (value) => value ? formatDate(value) : '-',
    },
  ];

  return (
    <MainLayout>
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Patients</h1>
            <p className="text-gray-600">Manage your patient database</p>
          </div>
          <Button onClick={() => setAddModalOpen(true)}>+ Add Patient</Button>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <Card.Body>
            <Input
              placeholder="Search by name, email, or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              container="mb-0"
            />
          </Card.Body>
        </Card>

        {/* Table */}
        <Card>
          <Card.Body>
            {loading ? (
              <LoadingSpinner size="md" fullHeight={false} />
            ) : (
              <Table
                columns={columns}
                data={patients}
                isResponsive={true}
                onRowClick={(patient) => navigate(`/patients/${patient.id}`)}
              />
            )}
          </Card.Body>
        </Card>
      </div>

      {/* Add Patient Modal */}
      <Modal
        isOpen={addModalOpen}
        onClose={() => {
          setAddModalOpen(false);
          reset();
        }}
        title="Add New Patient"
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
              Add Patient
            </Button>
          </>
        }
      >
        <form className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="First Name"
              {...register('first_name', { required: 'First name is required' })}
              error={errors.first_name?.message}
              container="mb-0"
            />
            <Input
              label="Last Name"
              {...register('last_name', { required: 'Last name is required' })}
              error={errors.last_name?.message}
              container="mb-0"
            />
          </div>

          <Input
            label="Email (optional)"
            type="email"
            {...register('email', {
              validate: (v) => !v || validateEmail(v) || 'Invalid email',
            })}
            error={errors.email?.message}
            container="mb-0"
          />

          <Input
            label="Phone"
            type="tel"
            {...register('phone')}
            error={errors.phone?.message}
            container="mb-0"
          />

          <Input
            label="Date of Birth"
            type="date"
            {...register('date_of_birth')}
            error={errors.date_of_birth?.message}
            container="mb-0"
          />

          <Textarea
            label="Notes"
            {...register('notes')}
            error={errors.notes?.message}
            container="mb-0"
          />
        </form>
      </Modal>
    </MainLayout>
  );
};

export default Patients;
