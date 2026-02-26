# 🚀 Dental Pro - Quick Start Guide

Welcome to the Dental Pro React Dashboard! This is a production-ready SaaS admin panel for dental clinic management.

## 📦 What You Get

✅ **Complete React App** - All files ready to run  
✅ **Modern Tech Stack** - Vite, React 18, Tailwind CSS  
✅ **JWT Authentication** - With HttpOnly cookies & interceptors  
✅ **Protected Routes** - Role-based access control  
✅ **Responsive Design** - Mobile-first, beautiful UI  
✅ **Reusable Components** - Button, Card, Modal, Table, Avatar, Badge, etc.  
✅ **Custom Hooks** - useAuth, useAsync, useToast  
✅ **API Integration** - Pre-configured Axios with error handling  
✅ **State Management** - Zustand for lightweight state  
✅ **Form Handling** - React Hook Form with validation  
✅ **Toast Notifications** - React Hot Toast integration  

## ⚡ 60-Second Setup

```bash
# 1. Navigate to frontend
cd fe

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser
# http://localhost:5173
```

That's it! You now have a running Dental Pro dashboard.

## 🔐 Login

**Demo Account:**
- Email: `admin@dental.com`
- Password: `password123`

(Set these up in your Django admin first)

## 📁 File Structure Overview

```
fe/
├── src/
│   ├── components/        # Reusable UI components (Button, Card, etc)
│   ├── layouts/           # Page layouts (MainLayout, AuthLayout)
│   ├── pages/             # Full pages (Dashboard, Patients, etc)
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service with Axios
│   ├── store/             # Zustand state management
│   ├── utils/             # Helpers and Protected Routes
│   ├── index.css          # Global styles + Tailwind
│   ├── App.jsx            # Main app with routing
│   └── main.jsx           # Entry point
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── .env.example
├── README.md              # Detailed documentation
├── SETUP.md               # Setup & deployment guide
├── COMPONENTS.md          # Component library docs
└── .gitignore
```

## 🎯 Key Features

### 1. **Dashboard**
- Overview statistics
- Quick action buttons
- Today's schedule

### 2. **Patients**
- Search and filter patients
- Add new patient form
- Click to see detailed patient view
- Medical history
- Treatment history table
- Upload medical images

### 3. **Treatments**
- Filter by status (pending, completed, etc)
- Search by patient name
- Add treatment with modal
- Image upload support

### 4. **Settings**
- Clinic information
- Business hours
- Notification preferences
- Security options

### 5. **Profile**
- View user profile
- Edit personal information

### 6. **Responsive Navigation**
- Sidebar on desktop
- Mobile drawer navigation
- Profile dropdown menu
- Search bar in navbar

## 🔧 Customization

### Change Theme Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#your-color'
      }
    }
  }
}
```

### Add New Page

1. Create file: `src/pages/MyPage.jsx`
2. Add route in `src/App.jsx`
3. Add link in `src/components/Sidebar.jsx`

```jsx
// src/pages/MyPage.jsx
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';

export default function MyPage() {
  return (
    <MainLayout>
      <Card>
        <h1>My Page</h1>
      </Card>
    </MainLayout>
  );
}
```

### Add API Endpoint

Edit `src/services/api.js`:

```javascript
export const myService = {
  getAll: (params) => api.get('/my-endpoint/', { params }),
  create: (data) => api.post('/my-endpoint/', data),
};
```

## 📚 Component Examples

### Simple Form

```jsx
import Input from '../components/Input';
import Button from '../components/Button';
import { useForm } from 'react-hook-form';

export default function MyForm() {
  const { register, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input
        label="Email"
        type="email"
        {...register('email', { required: true })}
      />
      <Button type="submit">Submit</Button>
    </form>
  );
}
```

### Data Table

```jsx
import Table from '../components/Table';

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
];

<Table
  columns={columns}
  data={patients}
  onRowClick={(row) => console.log(row)}
  isResponsive={true}
/>
```

### Modal

```jsx
import Modal from '../components/Modal';
import Button from '../components/Button';
import { useState } from 'react';

export default function MyComponent() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>Open</Button>
      <Modal
        isOpen={open}
        onClose={() => setOpen(false)}
        title="My Modal"
      >
        Modal content here
      </Modal>
    </>
  );
}
```

## 🔄 Backend Integration

### API Base URL

Set in `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### JWT Authentication

Token is automatically added to requests:

```javascript
// Request
Authorization: Bearer <jwt_token>

// Response
{
  "user": { ...user_data },
  "access_token": "...",
  "refresh_token": "..."
}
```

### Error Handling

401 errors auto-logout user:

```javascript
// In src/services/api.js interceptor:
if (error.response?.status === 401) {
  logout();
  navigate('/login');
}
```

## 🧪 Testing in Browser

### DevTools Shortcuts

- Open DevTools: `F12`
- Mobile view: `Ctrl+Shift+M`
- React DevTools: Install extension from Chrome Store
- Performance: DevTools > Performance tab

### Test Responsive Design

1. Open DevTools (`F12`)
2. Click device toggle (`Ctrl+Shift+M`)
3. Select device or custom size
4. Test on: 320px, 375px, 768px, 1024px, 1440px

## 🚀 Production Build

```bash
# Build
npm run build

# Preview
npm run preview

# Deploy to Vercel
npm i -g vercel
vercel
```

Output: `dist/` folder (ready to deploy)

## 🎨 UI Design Features

✨ **Modern Design**
- Soft shadows and rounded corners
- Consistent spacing (4px grid)
- Professional color palette
- Smooth transitions

📱 **Responsive**
- Mobile-first approach
- Tablet breakpoints
- Desktop optimization
- Touch-friendly buttons

🎯 **User Experience**
- Loading states throughout
- Toast notifications
- Form validation
- Error messages
- Empty states

## 🔐 Security Features

🔒 **Authentication**
- JWT tokens with Bearer scheme
- HttpOnly cookie support
- Auto-logout on expiry
- Request interceptors

🛡️ **Protected Routes**
- ProtectedRoute wrapper
- Role-based access (admin, staff, etc)
- Redirects to login if unauthorized

🚫 **Error Handling**
- 401 auto-logout
- User-friendly error messages
- API error boundaries

## 📊 State Management

### Zustand Stores

**Auth Store** (`src/store/authStore.js`)
- User data
- Authentication state
- Error messages

**UI Store** (`src/store/uiStore.js`)
- Sidebar visibility
- Mobile menu state
- Search query

## 🧩 Component Hierarchy

```
App (routing)
├── Login (AuthLayout)
└── Protected Routes (MainLayout)
    ├── Sidebar
    │   └── Navigation
    ├── Navbar
    │   ├── Search
    │   └── Profile Menu
    └── Main Content
        ├── Cards
        ├── Tables
        ├── Forms
        ├── Modals
        └── Alerts
```

## 💡 Pro Tips

1. **Use LoadingSpinner** while fetching data
   ```jsx
   {loading ? <LoadingSpinner /> : <Content />}
   ```

2. **Show toast notifications** for feedback
   ```jsx
   const { success, error } = useToast();
   ```

3. **Validate forms** before submission
   ```jsx
   {...register('email', { required: 'Required' })}
   ```

4. **Keep components small** (< 300 lines)

5. **Use custom hooks** for reusable logic

6. **Leverage Tailwind utilities** for styling

7. **Test on mobile** regularly

8. **Check browser console** for errors

## 📖 Documentation Files

1. **README.md** - Full feature documentation
2. **SETUP.md** - Installation & deployment guide
3. **COMPONENTS.md** - Component library reference
4. **This file** - Quick start guide

## 🆘 Troubleshooting

**CORS Error?**
- Check backend has CORS enabled for localhost:5173

**Login fails?**
- Create user in Django admin first
- Check API_BASE_URL in .env.local
- Look at network tab in DevTools

**Styles not showing?**
- Clear browser cache (Ctrl+Shift+Delete)
- Restart dev server

**Routes not working?**
- Check route paths match exactly
- Check sidebar navigation links match

## 🎓 Learning Path

1. Start with **README.md** for features
2. Check **SETUP.md** for installation
3. Read **COMPONENTS.md** for UI components
4. Review existing pages in `src/pages/`
5. Customize and extend!

## 🚀 Next Steps

1. ✅ Setup is complete
2. 📝 Add more pages to `src/pages/`
3. 🎨 Customize colors in `tailwind.config.js`
4. 🔌 Connect to your backend
5. 📱 Test responsiveness
6. 🚀 Deploy to production

## 📞 Support

- Backend docs: `../be/README.md`
- React docs: https://react.dev
- Tailwind docs: https://tailwindcss.com
- Vite docs: https://vitejs.dev

## 🎉 Success!

You now have a production-ready Dental Clinic Dashboard. The code is clean, scalable, and follows React best practices.

Happy coding! 🚀

---

**Questions or issues?** Check the documentation files or the component library guide.
