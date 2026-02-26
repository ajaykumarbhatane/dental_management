# Setup Instructions

## Quick Start

1. **Install Dependencies**
   ```bash
   cd fe
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env.local
   ```
   Update the `VITE_API_BASE_URL` to match your backend URL (default: http://localhost:8000/api)

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   Navigate to `http://localhost:5173`

## ⚡ Default Credentials (Demo)

- Email: `admin@dental.com`
- Password: `password123`

(Create these in your Django admin panel)

## 🔧 Configuration

### Backend Integration

The frontend connects to the Django backend at:
- Development: `http://localhost:8000/api`
- Production: Set in `.env.local`

### CORS Setup

Ensure your Django backend has CORS enabled:
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

### Cookie Settings

For JWT stored in HttpOnly cookies:
```python
# In settings.py
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
```

## 📦 Build & Deploy

### Build for Production
```bash
npm run build
```

Outputs to `dist/` folder

### Preview Build
```bash
npm run preview
```

### Deploy Options

**Vercel (Recommended)**
```bash
npm i -g vercel
vercel
```

**Netlify**
```bash
npm i -g netlify-cli
netlify deploy
```

**Static Server (Nginx)**
```bash
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/dental-pro;
    
    location / {
        try_files $uri /index.html;
    }
}
```

## 🎯 Usage Examples

### Adding a New Page

1. Create in `src/pages/MyPage.jsx`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/Sidebar.jsx`

```jsx
// src/pages/MyPage.jsx
import MainLayout from '../layouts/MainLayout';
import Card from '../components/Card';

export default function MyPage() {
  return (
    <MainLayout>
      <Card>
        <Card.Header>
          <h1>My Page</h1>
        </Card.Header>
        <Card.Body>
          Your content here
        </Card.Body>
      </Card>
    </MainLayout>
  );
}
```

### Creating a Custom Hook

```jsx
// src/hooks/useFetchPatients.js
import { useState, useEffect } from 'react';
import { patientService } from '../services/api';

export const useFetchPatients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const response = await patientService.getAll();
        setPatients(response.data);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  return { patients, loading };
};
```

### Making API Calls

```jsx
import { patientService } from '../services/api';
import { useToast } from '../hooks';

export default function MyComponent() {
  const { success, error } = useToast();

  const handleAddPatient = async (data) => {
    try {
      const response = await patientService.create(data);
      success('Patient added successfully!');
    } catch (err) {
      error('Failed to add patient');
    }
  };
}
```

## 🧪 Testing

(Add Jest/Vitest configuration as needed)

```bash
npm run test
```

## 🌐 Responsive Testing

Use Chrome DevTools to test responsive design:
1. Press `F12` to open DevTools
2. Click the device toggle icon (or press `Ctrl+Shift+M`)
3. Test on different screen sizes

Key breakpoints:
- Mobile: 320px, 375px, 425px
- Tablet: 768px, 1024px
- Desktop: 1440px+

## 🐛 Debugging

### Enable API Request Logging

Add to `src/services/api.js`:
```javascript
api.interceptors.request.use(req => {
  console.log('Request:', req);
  return req;
});
```

### Browser DevTools

1. React DevTools extension
2. Redux DevTools (if using Redux)
3. Network tab to inspect API calls
4. Console for errors and logs

## 🎨 Customizing Styles

Edit `src/index.css` and `tailwind.config.js` for global styles and theme colors.

## 📚 Useful Resources

- [React Docs](https://react.dev)
- [React Router Docs](https://reactrouter.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Hook Form Docs](https://react-hook-form.com)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Axios Docs](https://axios-http.com)

## ❓ Troubleshooting

**CORS Errors**
- Check backend has CORS enabled
- Verify API_BASE_URL in .env.local

**404 Routes**
- Check routes are defined in App.jsx
- Check sidebar navigation links match routes

**Styling Issues**
- Clear browser cache (Ctrl+Shift+Delete)
- Rebuild Tailwind CSS (might need vite restart)

**Auth Issues**
- Check cookies are being set in DevTools
- Verify backend returns correct JWT
- Check ProtectedRoute permissions

## 📞 Support

For backend-related issues, see `../be/README.md`
