# 🏗️ Architecture & Design Decisions

## Overview

This document explains the architectural choices and design patterns used in the Dental Pro React dashboard.

## 📐 Architecture Layers

```
┌─────────────────────────────────────┐
│      Pages (UI Layer)               │
│  Login, Dashboard, Patients, etc    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Components (UI Components)         │
│  Button, Card, Table, Modal, etc    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Hooks & Methods (Business Logic)  │
│  useAuth, useAsync, useToast        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Stores (State Management)          │
│  authStore, uiStore (Zustand)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Services (Data/API Layer)         │
│  Axios instance with interceptors   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Remote APIs (Django Backend)      │
│  /api/users, /api/patients, etc     │
└─────────────────────────────────────┘
```

## 🧩 Component Architecture

### Atomic Design Principles

Components are organized by complexity:

1. **Atoms** - Basic reusable components
   - Button, Badge, Avatar
   - Input, Textarea, Select
   - LoadingSpinner
   
2. **Molecules** - Simple component combinations
   - Card (with Header, Body, Footer)
   - Modal
   - FileUpload

3. **Organisms** - Complex components
   - Sidebar (with navigation)
   - Navbar (with profile menu)
   - Table (with data rendering)

4. **Templates** - Layout combinations
   - MainLayout (Sidebar + Navbar + Content)
   - AuthLayout (Centered form)

5. **Pages** - Full page components
   - Login, Dashboard, Patients
   - Treatments, Settings, Profile

### Composition Over Inheritance

All components use composition via props and children:

```jsx
// ✅ Good - Composition
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
</Card>

// ❌ Bad - Would be inheritance
<Card title="Title" body={<Content />} />
```

## 🔄 Data Flow

### Authentication Flow

```
User Input (Login Page)
    ↓
authService.login(email, password)
    ↓
Axios POST to /api/users/login/
    ↓
Backend validates & returns JWT + user data
    ↓
Store JWT in HttpOnly cookie (automatically via response)
    ↓
useAuthStore.setUser(userData)
    ↓
Redirect to /dashboard
    ↓
useAuth() hook fetches user on mount
    ↓
Protected routes check isAuthenticated
```

### Data Fetching Flow

```
Component Mount
    ↓
useEffect(() => { fetch data })
    ↓
API Service (axios)
    ↓
Request Interceptor adds Bearer token
    ↓
Backend returns data
    ↓
Response Interceptor handles 401
    ↓
State update (setPatients)
    ↓
Component re-render
```

### State Management Flow

```
User Interaction
    ↓
Event Handler
    ↓
Update Zustand Store
    ↓
Store notifies subscribers
    ↓
Components re-render
    ↓
UI updates
```

## 🏭 State Management Strategy

### Why Zustand Over Redux?

| Feature | Zustand | Redux | Winner |
|---------|---------|-------|--------|
| Boilerplate | Low | High | Zustand |
| Learning Curve | Gentle | Steep | Zustand |
| Bundle Size | 2.5KB | 17KB | Zustand |
| DevTools | Basic | Excellent | Redux |
| For Small Apps | Great | Overkill | Zustand |
| For Large Apps | Good | Better | Redux |

**Decision:** Zustand for medium-sized apps like Dental Pro

```javascript
// Example Zustand store
const useAuthStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

### Store Organization

**authStore.js** - Authentication
- user data
- isAuthenticated flag
- error messages

**uiStore.js** - UI State
- sidebar visibility
- mobile menu state
- search queries

### Anti-Patterns to Avoid

❌ **Don't:** Store everything in global state
✅ **Do:** Use component local state when possible

❌ **Don't:** Complex derived state in store
✅ **Do:** Calculate in components using selectors

## 🎣 Custom Hooks

### useAuth Hook

Purpose: Centralize authentication logic

```javascript
const useAuth = () => {
  // Initialize auth on mount
  // Handle login/logout
  // Return user, isAuthenticated, etc
};
```

Benefits:
- Reusable across pages
- Handles async operations
- Stores state in Zustand
- Cleaner components

### useAsync Hook

Purpose: Generic async operation handling

```javascript
const { execute, status, data, error } = useAsync(
  apiFunction,
  immediate // Run on mount?
);
```

Benefits:
- Manages loading state
- Handles errors
- Provides clean API
- Reusable pattern

### useToast Hook

Purpose: Notification helper

```javascript
const { success, error, loading } = useToast();
success('Done!');
```

Benefits:
- Consistent toast usage
- Type-safe variants
- Easy to maintain

## 🔌 API Service Layer

### Axios Configuration

**Base Setup:**
```javascript
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Include cookies
});
```

**Request Interceptor:**
- Adds JWT Bearer token from cookies
- Runs on every request automatically

**Response Interceptor:**
- Handles 401 errors (redirects to login)
- Logs errors for debugging

### Service Organization

```javascript
export const authService = {
  login: (email, password) => api.post('/users/login/', ...),
  logout: () => api.post('/users/logout/'),
};

export const patientService = {
  getAll: (params) => api.get('/patients/', { params }),
  create: (data) => api.post('/patients/', data),
};
```

Benefits:
- Centralized API methods
- Type-safe with proper naming
- Easy to mock for testing
- Single source of truth

## 🎨 Styling Strategy

### Tailwind CSS Configuration

**Custom Extensions:**
```javascript
colors: { primary, accent }    // Brand colors
boxShadow: { soft, soft-md }   // Depth
animation: { spin-slow }       // Custom animations
```

**Component Classes:**
```css
.btn-primary { /* predefined button styles */ }
.card { /* predefined card styles */ }
.input-field { /* predefined input styles */ }
```

### Responsive Design

**Breakpoints:**
- Mobile: < 640px (default)
- Tablet: 640px - 1024px (md)
- Desktop: > 1024px (lg, xl, 2xl)

**Mobile-First Approach:**
```jsx
<div className="block md:flex">
  Mobile (stacked) -> Tablet+ (flex)
</div>
```

## 🛣️ Routing Architecture

### Route Organization

```javascript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/dashboard" element={
    <ProtectedRoute><Dashboard /></ProtectedRoute>
  } />
  <Route path="/patients/:id" element={
    <ProtectedRoute><PatientDetail /></ProtectedRoute>
  } />
</Routes>
```

### Protected Routes

```javascript
<ProtectedRoute requiredRole="admin">
  <AdminPanel />
</ProtectedRoute>
```

Features:
- Check authentication
- Check user is initialized (prevents flashing)
- Optional role validation
- Redirect to login if unauthorized

## 📋 Form Handling

### React Hook Form Integration

```javascript
const { register, handleSubmit, formState: { errors } } = useForm({
  defaultValues: { /* ... */ }
});

<Input
  {...register('email', { 
    required: 'Email required',
    validate: isValidEmail 
  })}
  error={errors.email?.message}
/>
```

Benefits:
- Minimal re-renders (hook-based)
- Built-in validation
- Easy error handling
- Small bundle size

## 🔐 Security Considerations

### JWT Storage

**HttpOnly Cookies (Recommended):**
```javascript
// Backend sets:
Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict

// Frontend uses automatically:
// Browsers attach to requests automatically
// Not accessible via JavaScript (XSS protection)
```

### Axios Interceptor

```javascript
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### CORS & CSRF

**Backend Setup Required:**
```python
# Django settings
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]
```

## 🧪 Testing Strategy

### Unit Testing (Future)

Would test:
- Utility functions (helpers.js)
- Custom hooks (useAuth, useAsync)
- Components in isolation

```javascript
// Example: jest + React Testing Library
test('Button renders', () => {
  render(<Button>Click</Button>);
  expect(screen.getByText('Click')).toBeInTheDocument();
});
```

### Integration Testing (Future)

Would test:
- API flows with mock server
- Form submissions
- Navigation

### E2E Testing (Future)

Would test:
- Complete user journeys
- Multi-page interactions
- Real API integration

## 📊 Performance Optimizations

### Code Splitting

```javascript
// React.lazy + Suspense for route-based splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

<Suspense fallback={<LoadingSpinner />}>
  <Dashboard />
</Suspense>
```

### Component Optimization

- Memoization (React.memo) for pure components
- useMemo for expensive calculations
- useCallback for stable function references

### Bundle Optimization

- Tree-shaking unused imports
- Minification in production build
- Gzip compression on server

## 🚀 Scalability Considerations

### How to Scale This Architecture

**More Pages:**
- Add to `src/pages/`
- Update routing in `App.jsx`
- Add sidebar link

**More API Endpoints:**
- Add service in `src/services/api.js`
- Create custom fetch hooks
- Update components

**Complex State:**
- Add new Zustand store
- Use store composition
- Could migrate to Redux if needed

**More Components:**
- Keep components small (< 300 lines)
- Create component library folder
- Document with Storybook

## 📚 Code Organization Principles

1. **Single Responsibility**
   - Each file does one thing well
   - Components render, services fetch, hooks handle logic

2. **DRY (Don't Repeat Yourself)**
   - Reusable components in `/components`
   - Utilities in `/utils`
   - Services in `/services`

3. **Consistency**
   - Same naming conventions throughout
   - Similar component structures
   - Predictable folder structure

4. **Clarity**
   - Descriptive file/function names
   - Comments where complex
   - No magic numbers

## 🔄 Update & Maintenance Guide

### Updating Dependencies

```bash
npm outdated                 # See what's outdated
npm update                   # Update patches
npm install react@latest     # Update majors
```

### Adding New Component

```jsx
// src/components/MyComponent.jsx
export default function MyComponent({ prop1, prop2 }) {
  return <div>{prop1}</div>;
}
```

```javascript
// Add to exports if creating library
export { default as MyComponent } from './MyComponent';
```

### Adding API Endpoint

```javascript
// src/services/api.js
export const myService = {
  method1: (params) => api.get('/endpoint/', { params }),
  method2: (data) => api.post('/endpoint/', data),
};
```

### Adding Page

1. Create `src/pages/MyPage.jsx`
2. Add route in `src/App.jsx`
3. Add navigation in `src/components/Sidebar.jsx`
4. Use `MainLayout` wrapper

## 🎯 Conclusion

This architecture prioritizes:
- **Simplicity** - Easy to understand and modify
- **Scalability** - Can grow without major refactoring
- **Maintainability** - Clear separation of concerns
- **Performance** - Optimized for user experience
- **Best Practices** - Follows React conventions

The code is production-ready and follows industry standards for modern React applications.
