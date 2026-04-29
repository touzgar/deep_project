# Troubleshooting Guide

## 🚨 Current Issue: Signup Failed

### Problem
- **Error**: "Signup failed. Please try again."
- **Console Errors**: 
  - 404 (Not Found) on `http://localhost:8000/api/v1/auth/signup`
  - CORS policy error

### Root Cause
**The backend server is not running!**

### Solution
Start the backend server:

#### Quick Fix (Windows):
1. **Double-click** `start-backend.bat` in the project root
2. Wait for "Uvicorn running on http://0.0.0.0:8000"
3. Try signing up again

#### Manual Fix:
```bash
# Open a new terminal
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔍 Common Issues & Solutions

### 1. Backend Not Running

**Symptoms**:
- 404 errors
- CORS errors
- "Failed to load resource"
- Cannot connect to server

**Solution**:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Visit http://localhost:8000 - should show welcome message

---

### 2. Port Already in Use

**Symptoms**:
- "Address already in use"
- "Port 8000 is already in use"

**Solution**:

**Windows**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Alternative**: Use a different port
```bash
uvicorn main:app --reload --port 8001
```
Then update `frontend/src/services/api.ts`:
```typescript
baseURL: 'http://localhost:8001/api/v1'
```

---

### 3. Module Not Found Errors

**Symptoms**:
- "No module named 'fastapi'"
- "No module named 'app'"
- "ModuleNotFoundError"

**Solution**:

**Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

**Make sure you're in the right directory**:
```bash
# Should be in backend/ directory
cd backend
python -m uvicorn main:app --reload
```

---

### 4. Database Connection Error

**Symptoms**:
- "Could not connect to database"
- "Connection refused"
- "Database does not exist"

**Solution**:

**Check PostgreSQL is running**:
```bash
# Windows - check if PostgreSQL service is running
sc query postgresql-x64-14
```

**Create database**:
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE attendance_db;

-- Exit
\q
```

**Run migrations**:
```bash
cd backend
alembic upgrade head
```

**Check .env file**:
```env
DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/attendance_db
```

---

### 5. CORS Errors (Backend Running)

**Symptoms**:
- Backend is running
- Still getting CORS errors

**Solution**:

**Check backend CORS configuration** in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart backend** after changes:
```bash
# Stop with Ctrl+C, then restart
python -m uvicorn main:app --reload
```

---

### 6. Frontend Not Loading

**Symptoms**:
- Blank page
- "Cannot GET /"
- Build errors

**Solution**:

**Install dependencies**:
```bash
cd frontend
npm install
```

**Start dev server**:
```bash
npm run dev
```

**Clear cache**:
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

### 7. API URL Mismatch

**Symptoms**:
- 404 on API calls
- Wrong endpoint

**Solution**:

**Check frontend API configuration** in `frontend/src/services/api.ts`:
```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // Should match backend
});
```

**Check backend is running on correct port**:
- Backend should be on port 8000
- Frontend should be on port 5173

---

### 8. Authentication Not Working

**Symptoms**:
- Login fails
- Token not saved
- Redirected to login repeatedly

**Solution**:

**Check browser console** for errors

**Clear localStorage**:
```javascript
// In browser console (F12)
localStorage.clear();
```

**Check token in localStorage**:
```javascript
// In browser console
console.log(localStorage.getItem('token'));
```

**Test login endpoint directly**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

---

### 9. Signup Validation Errors

**Symptoms**:
- "Email already registered"
- "Username already registered"
- Validation errors

**Solution**:

**Use different credentials**:
- Try a different email
- Try a different username

**Check database**:
```sql
-- Connect to database
psql -U admin -d attendance_db

-- Check existing users
SELECT username, email FROM users;
```

**Clear test data** (if needed):
```sql
-- CAUTION: This deletes all users!
DELETE FROM users WHERE email LIKE '%test%';
```

---

### 10. Password Strength Indicator Not Showing

**Symptoms**:
- Password strength bar not visible
- No color change

**Solution**:

**This is normal** - the indicator only shows when you type in the password field.

**Check if typing**:
- Start typing in the password field
- The bar should appear below

---

## 🔧 Development Setup Checklist

### Backend
- [ ] Python installed (3.8+)
- [ ] PostgreSQL installed and running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists
- [ ] Database created
- [ ] Migrations run (`alembic upgrade head`)
- [ ] Server running on port 8000
- [ ] Can access http://localhost:8000

### Frontend
- [ ] Node.js installed (16+)
- [ ] Dependencies installed (`npm install`)
- [ ] Dev server running on port 5173
- [ ] Can access http://localhost:5173
- [ ] API URL configured correctly

---

## 🧪 Testing the Setup

### 1. Test Backend
```bash
# Should return welcome message
curl http://localhost:8000

# Should return API docs
curl http://localhost:8000/docs
```

### 2. Test Signup Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "teacher"
  }'
```

### 3. Test Login Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 4. Test Frontend
1. Open http://localhost:5173
2. Should see landing page
3. Click "Sign Up"
4. Fill form and submit
5. Should redirect to login

---

## 📊 Debugging Tools

### Backend Debugging

**Check server logs**:
- Look at terminal where backend is running
- Shows all requests and errors

**Use Swagger UI**:
- Visit http://localhost:8000/docs
- Test endpoints directly in browser

**Check database**:
```bash
psql -U admin -d attendance_db
\dt  # List tables
SELECT * FROM users;  # View users
```

### Frontend Debugging

**Browser DevTools** (F12):
- **Console**: JavaScript errors
- **Network**: API requests and responses
- **Application**: localStorage, cookies

**React DevTools**:
- Install React DevTools extension
- Inspect component state

---

## 🆘 Still Stuck?

### Collect Information

1. **Backend logs**: Copy terminal output
2. **Frontend console**: Copy browser console errors
3. **Network tab**: Check failed requests
4. **Environment**: 
   - OS version
   - Python version (`python --version`)
   - Node version (`node --version`)
   - PostgreSQL version

### Check These Files

1. `backend/.env` - Database and secrets
2. `frontend/src/services/api.ts` - API URL
3. `backend/main.py` - CORS configuration
4. `backend/app/api/routers/auth.py` - Auth endpoints

### Common Mistakes

- ❌ Backend not running
- ❌ Wrong port numbers
- ❌ Database not created
- ❌ Missing .env file
- ❌ Wrong API URL in frontend
- ❌ Firewall blocking ports

---

## ✅ Success Indicators

### Backend Running Successfully
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Running Successfully
```
  VITE v5.2.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Successful Signup
- Form submits without errors
- Success message appears
- Redirects to login page
- User created in database

---

## 🎯 Quick Reference

### Start Everything
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Stop Everything
- Press `Ctrl+C` in each terminal

### Reset Everything
```bash
# Backend
cd backend
rm -rf __pycache__ app/__pycache__
alembic downgrade base
alembic upgrade head

# Frontend
cd frontend
rm -rf node_modules dist
npm install
```

---

**Remember**: Most issues are solved by ensuring the backend server is running! 🚀
