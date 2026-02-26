import React from 'react';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import { useForm } from 'react-hook-form';
import { useToast } from '../hooks';

const Settings = () => {
  const { success } = useToast();
  const { register, handleSubmit, reset } = useForm({
    defaultValues: {
      clinic_name: 'Smile Dental Clinic',
      clinic_address: '123 Main St, Springfield',
      clinic_phone: '+1 (555) 123-4567',
      clinic_email: 'info@smiledental.com',
      clinic_hours: '9:00 AM - 5:00 PM',
      clinic_description: 'A modern dental clinic...',
    },
  });

  const onSubmit = (data) => {
    console.log(data);
    success('Settings updated successfully');
  };

  return (
    <MainLayout>
      <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Manage your clinic information and preferences</p>
        </div>

        {/* Clinic Settings */}
        <Card className="max-w-2xl">
          <Card.Header>
            <h3 className="text-lg font-semibold text-gray-900">Clinic Information</h3>
          </Card.Header>
          <Card.Body>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <Input
                label="Clinic Name"
                {...register('clinic_name')}
              />

              <Input
                label="Address"
                {...register('clinic_address')}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Phone"
                  type="tel"
                  {...register('clinic_phone')}
                />
                <Input
                  label="Email"
                  type="email"
                  {...register('clinic_email')}
                />
              </div>

              <Input
                label="Business Hours"
                {...register('clinic_hours')}
              />

              <Textarea
                label="Clinic Description"
                {...register('clinic_description')}
              />

              <div className="flex gap-3">
                <Button type="submit">Save Changes</Button>
                <Button type="button" variant="secondary" onClick={() => reset()}>
                  Cancel
                </Button>
              </div>
            </form>
          </Card.Body>
        </Card>

        {/* Other Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Card>
            <Card.Header>
              <h3 className="font-semibold text-gray-900">Notifications</h3>
            </Card.Header>
            <Card.Body>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span className="text-gray-700">Email notifications</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span className="text-gray-700">Appointment reminders</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" className="w-4 h-4" />
                  <span className="text-gray-700">Marketing emails</span>
                </label>
              </div>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <h3 className="font-semibold text-gray-900">Security</h3>
            </Card.Header>
            <Card.Body className="space-y-3">
              <Button variant="secondary" className="w-full">
                Change Password
              </Button>
              <Button variant="secondary" className="w-full">
                Two-Factor Authentication
              </Button>
            </Card.Body>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default Settings;
