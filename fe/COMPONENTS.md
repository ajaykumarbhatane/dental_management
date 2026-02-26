# Component Library Documentation

## 📋 Overview

This document provides guidance on using all reusable components in the Dental Pro dashboard.

## 🪟 UI Components

### Button

```jsx
import Button from '@/components/Button';

// Basic usage
<Button>Click me</Button>

// Variants
<Button variant="primary">Primary</Button>        // Default blue
<Button variant="secondary">Secondary</Button>    // Gray
<Button variant="outline">Outline</Button>        // Border style
<Button variant="danger">Delete</Button>          // Red
<Button variant="ghost">Ghost</Button>            // No background

// Sizes
<Button size="sm">Small</Button>      // Small padding
<Button size="md">Medium</Button>     // Default
<Button size="lg">Large</Button>      // Large padding

// States
<Button disabled>Disabled</Button>
<Button loading>Loading</Button>

// Full width
<Button className="w-full">Full Width</Button>
```

### Input

```jsx
import Input from '@/components/Input';
import { useForm } from 'react-hook-form';

const { register, formState: { errors } } = useForm();

<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  {...register('email', { required: 'Email is required' })}
  error={errors.email?.message}
/>

// With helper text
<Input
  label="Password"
  type="password"
  helperText="At least 8 characters"
  {...register('password')}
/>

// Without label (container)
<Input
  placeholder="Search..."
  container="mb-0"
/>
```

### Select

```jsx
import Select from '@/components/Select';

<Select
  label="Treatment Type"
  options={[
    { value: 'cleaning', label: 'Cleaning' },
    { value: 'filling', label: 'Filling' },
  ]}
  {...register('treatment_type')}
/>
```

### Textarea

```jsx
import Textarea from '@/components/Textarea';

<Textarea
  label="Notes"
  rows={4}
  placeholder="Enter notes..."
  {...register('notes')}
/>
```

### Card

```jsx
import Card from '@/components/Card';

// Basic card
<Card>
  <p>Simple content</p>
</Card>

// With sections
<Card>
  <Card.Header>
    <h3>Title</h3>
  </Card.Header>
  <Card.Body>
    Main content
  </Card.Body>
  <Card.Footer>
    Footer content
  </Card.Footer>
</Card>

// With custom styling
<Card className="border-l-4 border-primary-600">
  Important card
</Card>
```

### Badge

```jsx
import Badge from '@/components/Badge';

<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="danger">Failed</Badge>
<Badge variant="info">Info</Badge>
```

### Modal

```jsx
import Modal from '@/components/Modal';
import { useState } from 'react';

export function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Modal Title"
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button>Confirm</Button>
          </>
        }
      >
        Modal content here
      </Modal>
    </>
  );
}
```

**Size options**: sm, md, lg, xl, 2xl

### Avatar

```jsx
import Avatar from '@/components/Avatar';

// With name (generates initials)
<Avatar name="John Doe" size="md" />

// With image
<Avatar name="John Doe" image="/path/to/image.jpg" size="lg" />

// With custom color
<Avatar name="Jane" size="sm" index={2} />
```

**Size options**: sm, md, lg, xl

### Table

```jsx
import Table from '@/components/Table';

const columns = [
  { key: 'name', label: 'Name' },
  { 
    key: 'status', 
    label: 'Status',
    render: (value) => <Badge variant={value}>{value}</Badge>
  },
  { 
    key: 'created_at', 
    label: 'Date',
    render: (value) => formatDate(value)
  },
];

<Table
  columns={columns}
  data={patients}
  loading={isLoading}
  isResponsive={true}
  onRowClick={(row) => console.log(row)}
  actions={(row) => (
    <Button size="sm" variant="outline" onClick={() => editPatient(row.id)}>
      Edit
    </Button>
  )}
/>
```

### FileUpload

```jsx
import FileUpload from '@/components/FileUpload';

<FileUpload
  label="Upload Image"
  onUpload={(file) => handleUpload(file)}
  accept="image/*"
  maxSize={5242880}
  helperText="Max 5MB"
  preview={true}
/>
```

### LoadingSpinner

```jsx
import LoadingSpinner from '@/components/LoadingSpinner';

// Full height spinner
<LoadingSpinner size="md" fullHeight={true} />

// Inline spinner
<LoadingSpinner size="sm" fullHeight={false} />
```

**Size options**: sm, md, lg

## 🎨 Layout Components

### MainLayout

```jsx
import MainLayout from '@/layouts/MainLayout';

<MainLayout>
  <h1>Dashboard Content</h1>
  <p>Your main content here</p>
</MainLayout>
```

Includes:
- Responsive sidebar (drawer on mobile)
- Top navbar with profile menu
- Auto-logout on token expiry

### AuthLayout

```jsx
import AuthLayout from '@/layouts/AuthLayout';

<AuthLayout>
  <form>
    <h2>Sign In</h2>
    {/* Form content */}
  </form>
</AuthLayout>
```

## 🔧 Custom Hooks

### useAuth

```jsx
import useAuth from '@/hooks/useAuth';

export function MyComponent() {
  const { user, isAuthenticated, isInitialized, login, logout } = useAuth();

  return (
    <>
      {isAuthenticated && <p>Welcome {user.first_name}!</p>}
      <button onClick={() => logout()}>Logout</button>
    </>
  );
}
```

### useAsync

```jsx
import { useAsync } from '@/hooks';
import { patientService } from '@/services/api';

export function PatientsList() {
  const { execute, status, data, error } = useAsync(
    patientService.getAll,
    false
  );

  useEffect(() => {
    execute();
  }, []);

  if (status === 'pending') return <LoadingSpinner />;
  if (error) return <p>Error: {error.message}</p>;
  
  return <div>{/* render data */}</div>;
}
```

### useToast

```jsx
import { useToast } from '@/hooks';

export function MyComponent() {
  const { success, error, loading } = useToast();

  const handleClick = async () => {
    const toast = loading('Processing...');
    try {
      await someAsyncOperation();
      success('Done!');
    } catch (err) {
      error('Failed!');
    }
  };

  return <button onClick={handleClick}>Submit</button>;
}
```

## 🎯 Utility Functions

### Formatting

```jsx
import {
  formatDate,
  formatTime,
  formatDatetime,
  truncate,
  getInitials,
  getTreatmentStatus,
} from '@/utils/helpers';

formatDate('2026-02-25')           // "Feb 25, 2026"
formatTime('14:30:00')             // "2:30 PM"
formatDatetime('2026-02-25T14:30') // "Feb 25, 2026 2:30 PM"
truncate('Long text...', 20)       // "Long text..."
getInitials('John', 'Doe')         // "JD"
getTreatmentStatus('completed')    // { color: 'success', label: 'Completed' }
```

### Validation

```jsx
import {
  validateEmail,
  validatePhone,
} from '@/utils/helpers';

validateEmail('user@example.com')  // true
validatePhone('+1 (555) 123-4567') // true
```

### Other

```jsx
import { cn, getAvatarColor } from '@/utils/helpers';

// Clsx wrapper for conditional classes
cn('text-red-500', isError && 'font-bold')

// Get color for avatar
getAvatarColor(0)  // 'bg-primary-500'
getAvatarColor(1)  // 'bg-pink-500'
```

## 🛠️ Zustand Stores

### useAuthStore

```jsx
import useAuthStore from '@/store/authStore';

export function MyComponent() {
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const logout = useAuthStore((state) => state.logout);

  return <div>{user?.first_name}</div>;
}
```

### useUIStore

```jsx
import useUIStore from '@/store/uiStore';

export function MyComponent() {
  const { sidebarOpen, toggleSidebar, searchQuery, setSearchQuery } = 
    useUIStore();

  return (
    <>
      <input
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button onClick={toggleSidebar}>Toggle</button>
    </>
  );
}
```

## 🔌 API Service

```jsx
import {
  authService,
  patientService,
  treatmentService,
  clinicService,
} from '@/services/api';

// Auth
authService.login(email, password)
authService.logout()
authService.me()

// Patients
patientService.getAll({ search: 'john' })
patientService.getById(id)
patientService.create(data)
patientService.update(id, data)
patientService.uploadImage(id, file)

// Treatments
treatmentService.getAll({ status: 'pending' })
treatmentService.create(data)

// Clinics
clinicService.getById(id)
```

## 📝 Form Example

```jsx
import { useForm } from 'react-hook-form';
import Input from '@/components/Input';
import Button from '@/components/Button';

export function PatientForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      first_name: '',
      email: '',
    },
  });

  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        label="First Name"
        {...register('first_name', { required: 'Required' })}
        error={errors.first_name?.message}
      />
      <Input
        label="Email"
        type="email"
        {...register('email', { 
          required: 'Required',
          pattern: { value: /.+@.+/, message: 'Invalid email' }
        })}
        error={errors.email?.message}
      />
      <Button type="submit">Submit</Button>
    </form>
  );
}
```

## 🎓 Best Practices

1. **Always handle loading states**
   ```jsx
   {loading ? <LoadingSpinner /> : <Content />}
   ```

2. **Show toast notifications**
   ```jsx
   const { success, error } = useToast();
   try { ... } catch { error('Failed!') }
   ```

3. **Use Protected Routes**
   ```jsx
   <ProtectedRoute requiredRole="admin">
     <AdminPanel />
   </ProtectedRoute>
   ```

4. **Validate forms**
   ```jsx
   {...register('email', { 
     required: 'Email required',
     validate: isValidEmail
   })}
   ```

5. **Set container="mb-0"** on inputs without margin
   ```jsx
   <Input container="mb-0" /> {/* For use in modals, etc */}
   ```

6. **Use responsive utilities**
   ```jsx
   <div className="hidden md:block">Desktop only</div>
   <div className="md:hidden">Mobile only</div>
   ```

7. **Keep components DRY**
   - Extract reusable components
   - Pass props instead of hardcoding
   - Use utility functions

## 🔍 Component Tree Example

```
App
├── Login (AuthLayout)
│   ├── Form
│   └── Buttons
└── Dashboard (MainLayout)
    ├── Sidebar
    │   └── Navigation Links
    ├── Navbar
    │   ├── Search Input
    │   └── Profile Menu (Modal)
    └── Main Content
        ├── Card
        │   ├── Card.Header
        │   ├── Card.Body
        │   └── Card.Footer
        └── Table
            ├── Avatar
            └── Badge
```
