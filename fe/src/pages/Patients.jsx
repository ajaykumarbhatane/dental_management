import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Modal from '../components/Modal';
import Table from '../components/Table';
import Textarea from '../components/Textarea';
import LoadingSpinner from '../components/LoadingSpinner';
import { patientService, userService } from '../services/api';
import useAuth from '../hooks/useAuth';
import { useToast } from '../hooks';
import { useForm } from 'react-hook-form';

const Patients = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { success, error: showError } = useToast();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [clinicDoctors, setClinicDoctors] = useState([]);

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
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
      assigned_doctor: '',
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

  // Load clinic doctors when opening the add modal
  useEffect(() => {
    if (addModalOpen) {
      userService.getDoctors()
        .then((res) => {
          // API response wrapper: { success, message, data: [...] }
          const docs = Array.isArray(res.data?.data) ? res.data.data : [];
          setClinicDoctors(docs);
          // if logged-in user is a doctor, preselect them
          const me = docs.find((d) => d.id === user?.id);
          if (me) {
            setValue('assigned_doctor', me.id);
          }
        })
        .catch(() => {});
    }
  }, [addModalOpen, user, setValue]);

  // Add new patient
  const onSubmit = async (data) => {
    setSubmitting(true);
    try {
      // Prepare patient creation payload
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
        assigned_doctor: data.assigned_doctor || null,
      };

      await patientService.create(payload);
      success('Patient created successfully');
      setAddModalOpen(false);
      reset();
      // Refresh list
      const response = await patientService.getAll({ search: searchQuery });
      setPatients(response.data.results || response.data);
    } catch (error) {
      const errorMsg = 
        error.response?.data?.error?.details ||
        error.response?.data?.error?.message ||
        error.response?.data?.detail ||
        'Failed to create patient';
      
      // If it's a details object with field errors, show a formatted message
      if (typeof errorMsg === 'object') {
        const fieldErrors = Object.entries(errorMsg)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages[0] : messages}`)
          .join('\n');
        showError(fieldErrors || 'Failed to create patient');
      } else {
        showError(errorMsg);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      key: 'first_name',
      label: 'Name',
      render: (value, row) => `${row.first_name} ${row.last_name}`.trim(),
    },
    {
      key: 'contact_number',
      label: 'Phone',
      render: (value) => value || '-',
    },
    {
      key: 'assigned_doctor',
      label: 'Assigned Doctor',
      render: (value, row) => row.doctor_name || '-',
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
          setClinicDoctors([]);
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
                setClinicDoctors([]);
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
            <div className="mt-3">
              <Select
                label="Assign Doctor"
                {...register('assigned_doctor')}
                error={errors.assigned_doctor?.message}
                container="mb-0"
              >
                <option value="">None</option>
                {clinicDoctors?.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.full_name || `${doc.first_name} ${doc.last_name}`}
                  </option>
                ))}
              </Select>
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

export default Patients;
