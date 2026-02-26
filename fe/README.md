# Dental Pro - React Frontend

A modern, production-grade React dashboard for dental clinic management built with Vite, Tailwind CSS, and best practices in mind.

## 🎯 Features

✅ **Modern Stack**
- React 18 with Vite for lightning-fast development
- Tailwind CSS for responsive, beautiful UI
- React Router for seamless navigation
- Zustand for lightweight state management
- Axios with JWT authentication interceptors

✅ **Security**
- JWT authentication with HttpOnly cookie support
- Protected routes with role-based access
- Auto logout on token expiry
- Request/Response interceptors

✅ **Responsive Design**
- Mobile-first approach
- Sidebar becomes drawer on mobile
- Tables convert to cards on small screens
- Touch-friendly navigation

✅ **Real-World Features**
- Patient management with search
- Treatment tracking with filters
- Medical history and image uploads
- Appointment scheduling (placeholder)
- Profile and clinic settings
- Loading states and error handling
- Toast notifications
- Form validation with React Hook Form

✅ **Scalable Architecture**
- Component-based design
- Custom hooks for logic reuse
- Service layer for API calls
- Centralized state management
- Utility functions for common operations

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.jsx
│   ├── Card.jsx
│   ├── Input.jsx
│   ├── Modal.jsx
│   ├── Table.jsx
│   ├── Avatar.jsx
│   ├── Badge.jsx
│   ├── LoadingSpinner.jsx
│   ├── FileUpload.jsx
│   ├── Sidebar.jsx
│   ├── Navbar.jsx
│   ├── Toast.jsx
│   └── ...
├── layouts/             # Page layouts
│   ├── MainLayout.jsx   # Sidebar + Navbar layout
│   └── AuthLayout.jsx   # Auth page layout
├── pages/               # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Patients.jsx
│   ├── PatientDetail.jsx
│   ├── Treatments.jsx
│   ├── Appointments.jsx
│   ├── Settings.jsx
│   └── Profile.jsx
├── hooks/               # Custom React hooks
│   ├── useAuth.js       # Authentication hook
│   └── index.js         # Other utility hooks
├── services/            # API services
│   └── api.js           # Axios instance with interceptors
├── store/               # State management (Zustand)
│   ├── authStore.js
│   └── uiStore.js
├── utils/               # Utility functions
│   ├── helpers.js       # Formatting, validation helpers
│   └── ProtectedRoute.jsx
├── index.css            # Global styles + Tailwind
├── App.jsx              # Main app component with routes
└── main.jsx             # Entry point
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
cd fe
npm install
```

### Environment Setup

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Update with your backend URL:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Dental Pro
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## 🏗️ Architecture Decisions

### 1. **State Management: Zustand**
- Lightweight and easy to use
- Less boilerplate than Redux
- Built-in middleware support
- Perfect for medium-sized apps

### 2. **Form Handling: React Hook Form**
- Minimal re-renders
- Easy integration with custom components
- Great validation support
- Smaller bundle size

### 3. **HTTP Client: Axios**
- Easy to use with interceptors
- Built-in request/response transformation
- Better error handling
- Industry standard

### 4. **Styling: Tailwind CSS**
- Utility-first CSS framework
- Highly customizable
- Great for responsive design
- Developer experience

### 5. **Component Architecture**
- Atomic design principles
- Composition over inheritance
- Reusable components with Props API
- Clear separation of concerns

## 🔐 Authentication Flow

```
1. User enters credentials on Login page
2. API call to backend with email/password
3. Backend returns JWT token + user data
4. Token stored in HttpOnly cookie
5. Axios interceptor adds Bearer token to requests
6. Protected routes check authentication
7. On 401, user is logged out and redirected to login
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md, lg)
- **Desktop**: > 1024px (xl, 2xl)

## 🎨 Custom Tailwind Config

- Primary colors: Sky blue (matching SaaS style)
- Accent colors: Pink for highlights
- Custom shadows for depth
- Rounded corners for modern look

## 🔧 Key Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| React | UI framework | 18.2.0 |
| React Router | Client routing | 6.20.0 |
| Axios | HTTP client | 1.6.2 |
| Zustand | State management | 4.4.0 |
| React Hook Form | Form management | 7.50.0 |
| React Hot Toast | Notifications | 2.4.1 |
| Tailwind CSS | Styling | 3.4.1 |
| js-cookie | Cookie management | 3.0.5 |

## 🧪 Best Practices Implemented

✅ Component composition over inheritance
✅ Prop drilling minimized with Context/Zustand
✅ Custom hooks for reusable logic
✅ Service layer for API abstraction
✅ Error boundaries (ready to add)
✅ Loading states throughout
✅ Form validation on client side
✅ Protected routes with role checking
✅ Toast notifications for feedback
✅ Responsive mobile-first design
✅ Clean, readable code
✅ Consistent naming conventions

## 📚 Component Examples

### Usage of Reusable Components

```jsx
// Button
<Button variant="primary" size="md" loading={isLoading}>
  Submit
</Button>

// Card
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer>Footer</Card.Footer>
</Card>

// Modal
<Modal isOpen={open} onClose={onClose} title="Title">
  Modal content here
</Modal>

// Table
<Table
  columns={columns}
  data={data}
  onRowClick={handleRowClick}
  isResponsive={true}
/>
```

## 🔄 Redux vs Zustand Decision

**Why Zustand over Redux?**
- Redux has more boilerplate (actions, reducers, selectors)
- Zustand is simpler for medium-sized apps
- Easier testing
- Better DX without Redux DevTools dependency
- Zustand is lighter (2.5KB vs 17KB for Redux)

For a larger app with complex state, consider Redux Toolkit.

## 🚀 Future Enhancements

- [ ] Add appointment scheduling with calendar
- [ ] Implement image gallery with lightbox
- [ ] Add notification bell with real-time updates
- [ ] Dark mode support
- [ ] Advanced search with filters
- [ ] PDF export for reports
- [ ] Multi-language support (i18n)
- [ ] Offline support with service workers

## 💡 Tips for Developers

1. Always use the API service layer in `services/api.js`
2. Create custom hooks in `hooks/` for reusable logic
3. Keep components under 300 lines
4. Use Zustand for global state
5. Leverage Tailwind's responsive utilities
6. Test with mobile first
7. Use LoadingSpinner while fetching data
8. Show toast notifications for user feedback
9. Validate forms before submission
10. Keep the component tree clean

## 📞 Support

For issues or questions, refer to the backend documentation in `../be/README.md`

## 📄 License

All rights reserved © 2026 Dental Pro
