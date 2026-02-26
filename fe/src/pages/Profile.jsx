import React from 'react';
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';
import Button from '../components/Button';
import Avatar from '../components/Avatar';
import useAuth from '../hooks/useAuth';
import { useForm } from 'react-hook-form';
import Input from '../components/Input';

const Profile = () => {
  const { user } = useAuth();
  const { register, handleSubmit } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
    },
  });

  return (
    <MainLayout>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile</h1>

        <div className="max-w-2xl">
          <Card className="mb-6">
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
            </Card.Header>
            <Card.Body>
              <div className="flex items-center gap-6 mb-6 pb-6 border-b border-gray-200">
                <Avatar
                  name={`${user?.first_name} ${user?.last_name}`}
                  size="lg"
                />
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </h4>
                  <p className="text-gray-600">{user?.email}</p>
                  <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
                </div>
              </div>

              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="First Name"
                    {...register('first_name')}
                  />
                  <Input
                    label="Last Name"
                    {...register('last_name')}
                  />
                </div>

                <Input
                  label="Email"
                  type="email"
                  {...register('email')}
                />

                <div className="flex gap-3">
                  <Button type="submit">Save Changes</Button>
                  <Button type="button" variant="secondary">Cancel</Button>
                </div>
              </form>
            </Card.Body>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default Profile;
