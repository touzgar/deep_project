# 🚀 QUICK FIX - Run These Commands

## Problem Found
The frontend Docker build is failing because:
- `npm ci --only=production` skips devDependencies
- TypeScript and Vite are in devDependencies
- Build needs these packages to compile

## ✅ I Fixed
- Updated `frontend/Dockerfile` to install ALL dependencies (including dev)
- This will allow TypeScript and Vite to run during build

## 📋 Run These Commands in Ubuntu (WSL2)

```bash
# 1. Navigate to project
cd /mnt/c/Users/user/Desktop/deep_project

# 2. Stop containers
docker-compose down

# 3. Remove old images (IMPORTANT!)
docker rmi deep_project-frontend deep_project-backend

# 4. Clear Docker build cache
docker builder prune -f

# 5. Rebuild with no cache (this will take 3-5 minutes)
docker-compose build --no-cache

# 6. Start containers
docker-compose up -d

# 7. Wait 30 seconds
sleep 30

# 8. Check status
docker ps

# 9. Test backend
curl http://localhost:8000

# 10. Open browser to http://localhost:3001
```

## ⚠️ IMPORTANT
After step 5 (rebuild), you should see:
- ✅ No "tsc: not found" error
- ✅ Frontend builds successfully
- ✅ Both images created

If you still see "tsc: not found", STOP and share the full error output.

## 🔍 Verify It's Working

### Test 1: Check Backend
```bash
curl http://localhost:8000
```
Should return: `{"message":"Welcome to Smart Face Attendance System API"}`

### Test 2: Check Frontend Container
```bash
docker exec attendance_frontend ls -la /usr/share/nginx/html/assets
```
Should show multiple .js and .css files

### Test 3: Open Browser
Go to: http://localhost:3001
- Should see your signup page
- Try creating an account
- Should NOT see "Not Found" error

## 🐛 If Still Not Working

### Check Build Logs
```bash
docker-compose build --no-cache 2>&1 | tee build.log
```
This saves the build output to `build.log` file.

### Check Container Logs
```bash
# Frontend logs
docker logs attendance_frontend

# Backend logs  
docker logs attendance_backend
```

### Check What's Running
```bash
docker ps -a
```

### Nuclear Option (Clean Everything)
```bash
# Stop everything
docker-compose down

# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)

# Remove all build cache
docker builder prune -af

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 📝 What Changed

### File: `frontend/Dockerfile`
**Before:**
```dockerfile
RUN npm ci --only=production  # ❌ Skips devDependencies
```

**After:**
```dockerfile
RUN npm ci  # ✅ Installs ALL dependencies including TypeScript
```

This is the KEY fix that will solve the "tsc: not found" error.
