# ⚡ Quick Start - 5 Minutes

## 🎯 What Was Fixed

✅ **djangorestframework-simplejwt**: `5.3.2` → `5.3.1` *(version fixed)*  
✅ **Database**: PostgreSQL → **SQLite** *(no setup needed)*  
✅ **Settings.py**: Updated to handle SQLite properly  
✅ **.env.example**: Uses SQLite by default  

**No external database setup needed! Everything works out of the box.**

---

## 🚀 Backend Setup (Django) - 3 Steps

### Terminal 1 - Backend

```bash
# 1. Go to backend folder
cd be

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies (now fixed!)
pip install -r requirements.txt

# 4. Setup database
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser

# 5. Create demo data (optional)
python manage.py shell
>>> from apps.clinics.models import Clinic
>>> Clinic.objects.create(name="Demo Clinic", contact_number="+1234567890")
>>> exit()

# 6. Start server
python manage.py runserver
```

✅ **Backend running at:** `http://localhost:8000`

---

## 💻 Frontend Setup (React) - 3 Steps

### Terminal 2 - Frontend (NEW TERMINAL)

```bash
# 1. Go to frontend folder
cd fe

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

✅ **Frontend running at:** `http://localhost:5173`

---

## 🔓 Login Credentials

Use the superuser you created:

```
Email: admin@dental.com (or your email)
Password: AdminPass123! (your password)
```

---

## ✅ Verification

Open `http://localhost:5173` in your browser:

- ✅ See login page
- ✅ Login works
- ✅ Dashboard displays
- ✅ Can navigate pages

---

## 🌐 URLs Reference

| What | Where |
|------|-------|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Django Admin | http://localhost:8000/admin/ |
| API Docs | http://localhost:8000/api/docs/ |

---

## ❌ If Something Goes Wrong

### Django doesn't start?
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### Port already in use?
```bash
# Backend on different port
python manage.py runserver 8001

# Frontend on different port
npm run dev -- --port 5174
```

### Clear everything and restart?
```bash
# Backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend
rm -rf node_modules
npm install
npm run dev
```

---

## 📚 Documentation

- **Full Setup**: `FULL_SETUP_GUIDE.md`
- **Frontend**: `fe/START_HERE.md` or `fe/QUICKSTART.md`
- **Backend**: `be/README.md`

---

**You're all set! 🎉**
