# 🔧 Restart Local Backend

## You're Running Backend Locally (Not in Docker)

Your logs show:
```
INFO: 127.0.0.1:61439 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

This means the backend is running on your local machine (not in Docker container).

## How to Restart Local Backend

### Step 1: Find the terminal running the backend
Look for a terminal window running:
- `uvicorn main:app`
- `python main.py`
- `npm run dev` (in backend folder)

### Step 2: Stop it
Press `Ctrl + C` in that terminal

### Step 3: Restart it
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test
Open browser: http://localhost:5173
Try to login - should work now!

## OR Use Docker Backend Instead

If you want to use Docker backend:

### Step 1: Stop local backend
Press `Ctrl + C` in the terminal running it

### Step 2: Rebuild and start Docker backend
```bash
cd /mnt/c/Users/user/Desktop/deep_project
docker-compose stop backend
docker rm attendance_backend
docker rmi deep_project-backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Step 3: Test
```bash
curl http://localhost:8000
```

Should return: `{"message":"Welcome to Smart Face Attendance System API"}`

### Step 4: Open browser
http://localhost:5173
Try to login - should work!

## How to Know Which Backend You're Using

### Local Backend:
- Logs show: `INFO: 127.0.0.1:xxxxx`
- Started with: `uvicorn main:app`
- Changes appear immediately (hot reload)

### Docker Backend:
- Logs show: `INFO: 172.x.x.x:xxxxx`
- Started with: `docker-compose up -d backend`
- Need to rebuild for changes: `docker-compose build backend`

## Check What's Running

```bash
# Check Docker containers
docker ps

# Check local processes (Windows)
netstat -ano | findstr ":8000"

# Check local processes (Linux/WSL)
lsof -i :8000
```
