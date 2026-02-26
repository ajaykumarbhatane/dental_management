# 🚀 Complete Setup Guide - Dental Pro Dashboard

This guide covers setting up both the **Django Backend** and **React Frontend**.

---

## ⚠️ Fixed Issues

✅ **Updated** `djangorestframework-simplejwt==5.3.1` (was 5.3.2 - doesn't exist)  
✅ **Updated** `.env.example` to use **SQLite for development** (no PostgreSQL setup needed)  
✅ **All configuration** updated and tested

---

## 🔧 Part 1: Backend Setup (Django)

### Step 1: Navigate to Backend

```bash
cd be/
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# On Windows, use:
# venv\Scripts\activate
```

### Step 3: Install Dependencies (Fixed Version)

```bash
pip install -r requirements.txt
```

✅ This now installs the correct `djangorestframework-simplejwt==5.3.1`

### Step 4: Configure Environment

```bash
# Copy example to actual file
cp .env.example .env

# The .env file is now configured for SQLite (no PostgreSQL needed!)
# You can review it but no changes needed for development:
cat .env
```

**Default .env for development:**
```
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Step 5: Run Migrations

```bash
# Create database and tables
python manage.py makemigrations
python manage.py migrate
```

✅ Creates `db.sqlite3` in your project root

### Step 6: Create Admin User

```bash
python manage.py createsuperuser
```

**Enter these details (or use your own):**
```
Email: admin@dental.com
Password: AdminPass123!
Password (again): AdminPass123!
```

### Step 7: Start Backend Server

```bash
python manage.py runserver
```

**Backend is now running at:**
```
http://localhost:8000
API Endpoints: http://localhost:8000/api/
Admin Panel: http://localhost:8000/admin/
API Docs (Swagger): http://localhost:8000/api/docs/
```

---

## 🎨 Part 2: Frontend Setup (React)

### Step 1: Open New Terminal

Keep the backend running in the first terminal, open a NEW terminal for the frontend.

### Step 2: Navigate to Frontend

```bash
cd fe/
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Configure Environment (Optional)

```bash
# Copy example
cp .env.example .env.local

# It's already set to http://localhost:8000/api
# No changes needed for local development
cat .env.local
```

### Step 5: Start Frontend Development Server

```bash
npm run dev
```

**Frontend is now running at:**
```
http://localhost:5173
```

---

## ✅ Verification Checklist

### Backend ✓

- [ ] Migrations completed successfully
- [ ] Admin user created
- [ ] Backend running on `http://localhost:8000`
- [ ] Can access `http://localhost:8000/admin/` (login with credentials)
- [ ] API docs visible at `http://localhost:8000/api/docs/`

### Frontend ✓

- [ ] Dependencies installed
- [ ] Frontend running on `http://localhost:5173`
- [ ] Page loads without errors
- [ ] Console shows no critical errors

---

## 🔐 Testing the Full Stack

### 1. Create a Test Patient

#### Via Django Admin:

1. Go to `http://localhost:8000/admin/`
2. Login with your superuser (admin@dental.com)
3. Click "Clinics" → Create clinic with name "Demo Clinic"
4. Click "CustomUsers" → Create patient:
   - Email: `patient@dental.com`
   - Password: `PatientPass123!`
   - Clinic: Demo Clinic
   - Role: PATIENT
5. Click Save

#### Or Via API (using cURL):

```bash
# Register new clinic admin
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@dental.com",
    "password": "DoctorPass123!",
    "password_confirm": "DoctorPass123!",
    "first_name": "John",
    "last_name": "Doe",
    "clinic_name": "Demo Clinic",
    "role": "ADMIN"
  }'
```

### 2. Login in Frontend

1. Open `http://localhost:5173`
2. Email: `doctor@dental.com` (or your created user)
3. Password: `DoctorPass123!` (your password)
4. ✅ Should see Dashboard

### 3. Test Features

- Navigate to Patients page
- Try adding a patient
- Check Treatments page
- Use the Settings page

---

## 🛠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'django'`

**Solution:** Activate virtual environment
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Issue: `django.db.ProgrammingError` or database errors

**Solution:** Re-run migrations
```bash
python manage.py migrate --run-syncdb
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Run on different port
python manage.py runserver 8001
```

### Issue: `CORS errors` or `Failed to fetch` in frontend

**Solution:** Ensure backend is running on `http://localhost:8000`

```bash
# Check if backend is running
curl http://localhost:8000/api/
```

### Issue: `npm install` fails

**Solution:** Clear cache and retry
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue: Frontend shows blank page

**Solution:** Check browser console for errors (F12)
- Clear browser cache (Ctrl+Shift+Delete)
- Restart frontend (`Ctrl+C`, then `npm run dev`)

---

## 📋 Quick Start Commands Summary

**Backend (Terminal 1):**
```bash
cd be
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Frontend (Terminal 2):**
```bash
cd fe
npm install
cp .env.example .env.local
npm run dev
```

---

## 🌐 Accessing the Application

After both servers are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React Dashboard |
| **Backend API** | http://localhost:8000/api/ | REST API endpoints |
| **Django Admin** | http://localhost:8000/admin/ | User & data management |
| **API Docs** | http://localhost:8000/api/docs/ | Interactive Swagger UI |

---

## 📚 Next Steps

### 1. **Create Demo Data**
- Add clinics via Django admin
- Create users (doctors, patients)
- Add sample treatments

### 2. **Test Features**
- Login with different user roles
- Test CRUD operations
- Try filtering/searching

### 3. **Customize**
- Change theme colors in `fe/tailwind.config.js`
- Add more pages/features
- Modify database models if needed

### 4. **Deploy** (Future)
- See `fe/SETUP.md` for React deployment
- See `be/README.md` for Django deployment

---

## 🔐 Important Security Notes

### Development Setup:
- ✅ SQLite database (development only)
- ✅ DEBUG=True (for development)
- ✅ Hardcoded SECRET_KEY (not secure)

### Before Production:
- ⚠️ Switch to PostgreSQL database
- ⚠️ Set DEBUG=False
- ⚠️ Generate new SECRET_KEY
- ⚠️ Configure ALLOWED_HOSTS
- ⚠️ Set up HTTPS/SSL
- ⚠️ Configure proper email backend

---

## 📞 Getting Help

### For Backend Issues:
- Check `be/README.md` for API documentation
- See Django logs in terminal
- Check database with Django admin

### For Frontend Issues:
- Check `fe/README.md` and `fe/QUICKSTART.md`
- Open browser DevTools (F12)
- Check network requests in DevTools

### For Integration Issues:
- Ensure both servers are running
- Check CORS configuration
- Verify API URL in frontend `.env.local`

---

## ✨ Success Indicators

✅ Backend running (no errors in terminal)  
✅ Frontend running (page loads)  
✅ Can login (with created credentials)  
✅ Dashboard displays stats  
✅ Can navigate between pages  
✅ Network requests work (DevTools shows 200 status)

---

**Everything is ready! Start with the commands above. 🚀**

Need more help? Check the individual README files:
- Backend: `be/README.md`
- Frontend: `fe/README.md` and `fe/QUICKSTART.md`
