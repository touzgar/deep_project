# ✅ COMPLETE FIX - Step by Step

## The Real Problem

"Login failed. Please check your credentials" means:
- ✅ CORS is working (request reaches backend)
- ✅ Backend is working (returns response)
- ❌ You don't have a user account yet!

You need to **SIGNUP FIRST** before you can login!

## Solution - Create an Account First

### Step 1: Open Signup Page
Go to: http://localhost:5173/signup

### Step 2: Create an Account
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`
- Account Type: `Administrator`
- Click "Create Account"

### Step 3: Login
After signup, you'll be redirected to login page.
- Username: `admin`
- Password: `admin123`
- Click "Sign In"

### Step 4: Success!
You should now be logged in and see the dashboard!

## OR Use the Test Script

Run this in Ubuntu to create a test user automatically:

```bash
cd /mnt/c/Users/user/Desktop/deep_project
chmod +x test_auth.sh
./test_auth.sh
```

This will:
1. Check if backend is running
2. Create a test user (admin/admin123)
3. Test login
4. Test CORS

Then you can login in the browser with:
- Username: `admin`
- Password: `admin123`

## Verify Everything Works

### 1. Backend Running
```bash
curl http://localhost:8000
```
Should return: `{"message":"Welcome to Smart Face Attendance System API"}`

### 2. Signup Works
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123","role":"teacher"}'
```
Should return user data with email

### 3. Login Works
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123"
```
Should return: `{"access_token":"...","token_type":"bearer"}`

### 4. Frontend Works
- Open: http://localhost:5173
- Should see login/signup pages
- No CORS errors in console (F12)

## Common Issues

### Issue 1: "Email already registered"
**Solution**: User already exists, just login with those credentials

### Issue 2: "Login failed"
**Solution**: Make sure you signed up first, or use correct credentials

### Issue 3: CORS errors
**Solution**: Restart backend after code changes
```bash
# If using Docker:
docker-compose restart backend

# If running locally:
# Press Ctrl+C and restart with:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 4: "Connection refused"
**Solution**: Backend is not running
```bash
# Start Docker backend:
docker-compose up -d backend

# OR start locally:
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Summary

**The Problem**: You were trying to login without having an account

**The Solution**: 
1. Go to http://localhost:5173/signup
2. Create an account
3. Then login with those credentials

**OR**: Run `./test_auth.sh` to create test user automatically

**Result**: You can now login and use the application!

## Quick Start

```bash
# 1. Make sure backend is running
docker ps  # Should see attendance_backend

# 2. Create test user
cd /mnt/c/Users/user/Desktop/deep_project
chmod +x test_auth.sh
./test_auth.sh

# 3. Open browser
# Go to: http://localhost:5173/login
# Username: admin
# Password: admin123
# Click "Sign In"

# 4. Success! You're in the dashboard!
```
