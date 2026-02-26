import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import AuthLayout from '../layouts/AuthLayout';
import Button from '../components/Button';
import Input from '../components/Input';
import useAuth from '../hooks/useAuth';
import { useToast } from '../hooks';
import { validateEmail } from '../utils/helpers';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error: showError } = useToast();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await login(data.email, data.password);
      success('Login successful!');
      navigate('/dashboard');
    } catch (err) {
      showError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Welcome Back</h2>
          <p className="text-gray-600 mt-1">Sign in to your account</p>
        </div>

        <Input
          label="Email Address"
          type="email"
          placeholder="you@example.com"
          {...register('email', {
            required: 'Email is required',
            validate: (value) => validateEmail(value) || 'Invalid email',
          })}
          error={errors.email?.message}
        />

        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          {...register('password', {
            required: 'Password is required',
            minLength: {
              value: 6,
              message: 'Password must be at least 6 characters',
            },
          })}
          error={errors.password?.message}
        />

        <Button
          type="submit"
          className="w-full"
          loading={loading}
        >
          Sign In
        </Button>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Demo credentials:
            <br />
            <code className="bg-gray-100 px-2 py-1 rounded">admin@dental.com / password123</code>
          </p>
        </div>
      </form>
    </AuthLayout>
  );
};

export default Login;
