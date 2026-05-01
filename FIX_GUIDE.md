# 🔧 Fix Guide - "Not Found" Error

## Problem
You're seeing a "Not Found" error when trying to signup because:
1. The frontend can't connect to the backend API
2. The API URL wasn't properly set during the Docker build
3. CORS wasn't configured for port 3001

## What I Fixed
✅ Updated `frontend/Dockerfile` to accept API URL as build argument
✅ Updated `docker-compose.yml` to pass the correct API URL during build
✅ Updated `backend/app/core/config.py` to allow CORS from port 3001
✅ Created rebuild scripts to make it easy for you

## How to Fix (Choose ONE method)

### Method 1: Using Ubuntu (WSL2) - RECOMMENDED

1. Open Ubuntu terminal
2. Navigate to your project:
   ```bash
   cd /mnt/c/Users/user/Desktop/deep_project
   ```

3. Run the rebuild script:
   ```bash
   chmod +x rebuild.sh
   ./rebuild.sh
   ```

4. Wait for it to complete (about 2-3 minutes)

5. Open your browser and go to: **http://localhost:3001**

### Method 2: Manual Commands in Ubuntu

```bash
# Navigate to project
cd /mnt/c/Users/user/Desktop/deep_project

# Stop containers
docker-compose down

# Remove old images
docker rmi attendance_frontend attendance_backend

# Rebuild with no cache
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Wait 30 seconds
sleep 30

# Check status
docker ps
```

### Method 3: Using Windows Command Prompt

1. Open Command Prompt as Administrator
2. Navigate to your project:
   ```cmd
   cd C:\Users\user\Desktop\deep_project
   ```

3. Run the batch file:
   ```cmd
   rebuild.bat
   ```

## After Rebuilding

### Test Backend
```bash
curl http://localhost:8000
```
Should return: `{"message":"Welcome to Smart Face Attendance System API"}`

### Test Frontend
Open browser: **http://localhost:3001**
- You should see the signup page
- Try creating an account
- The "Not Found" error should be gone

## Troubleshooting

### If you still see "Not Found":

1. **Check container logs:**
   ```bash
   docker logs attendance_frontend
   docker logs attendance_backend
   ```

2. **Check if containers are running:**
   ```bash
   docker ps
   ```
   You should see:
   - attendance_frontend (port 3001:80)
   - attendance_backend (port 8000:8000)

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for any red errors
   - Check Network tab for failed requests

4. **Verify API URL in browser:**
   - Open DevTools (F12)
   - Go to Console tab
   - Type: `localStorage.clear()`
   - Refresh the page
   - Try signup again

### If port 3001 is also taken:

Edit `docker-compose.yml` and change:
```yaml
ports:
  - "3002:80"  # Change 3001 to 3002
```

Then rebuild:
```bash
docker-compose down
docker-compose up -d --build
```

## What Changed

### Files Modified:
1. `frontend/Dockerfile` - Now accepts VITE_API_URL as build argument
2. `docker-compose.yml` - Passes API URL during build
3. `backend/app/core/config.py` - Added port 3001 to CORS origins

### New Files Created:
1. `rebuild.sh` - Linux/Mac rebuild script
2. `rebuild.bat` - Windows rebuild script
3. `FIX_GUIDE.md` - This guide

## Expected Result

After rebuilding:
- ✅ Frontend loads at http://localhost:3001
- ✅ Backend API works at http://localhost:8000
- ✅ Signup page works without "Not Found" error
- ✅ You can create accounts and login
- ✅ All features work properly

## Need More Help?

If you're still having issues, run these commands and share the output:

```bash
# Check Docker status
docker ps

# Check frontend logs
docker logs attendance_frontend --tail 50

# Check backend logs
docker logs attendance_backend --tail 50

# Test API directly
curl http://localhost:8000
curl http://localhost:8000/api/v1/auth/signup -X POST -H "Content-Type: application/json" -d '{"username":"test","email":"test@test.com","password":"test123","role":"teacher"}'
```
