import os

pages_dir = 'frontend/src/pages'
components_dir = 'frontend/src/components'

os.makedirs(pages_dir, exist_ok=True)
os.makedirs(components_dir, exist_ok=True)

pages = {
    'Classes.tsx': '''import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Classes() {
    const [classes, setClasses] = useState([]);
    
    useEffect(() => {
        const fetchClasses = async () => {
            try {
                const res = await api.get('/classes/');
                setClasses(res.data);
            } catch (err) {
                console.error("Failed to load classes", err);
            }
        };
        fetchClasses();
    }, []);

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Classes Management</h1>
            <div className="bg-white shadow rounded-lg p-4">
                <table className="w-full text-left">
                    <thead><tr><th>Name</th><th>Description</th></tr></thead>
                    <tbody>
                        {classes.map((cls: any) => (
                            <tr key={cls.id}>
                                <td>{cls.name}</td>
                                <td>{cls.description}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}''',
    
    'Sessions.tsx': '''import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Sessions() {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Sessions Management</h1>
            <p>Sessions will be managed here.</p>
        </div>
    );
}''',

    'LiveCamera.tsx': '''import React from 'react';

export default function LiveCamera() {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Live Camera Attendance</h1>
            <div className="aspect-video bg-gray-900 rounded flex items-center justify-center text-white">
                Camera Feed Simulation
            </div>
        </div>
    );
}''',

    'Reports.tsx': '''import React from 'react';

export default function Reports() {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Reports</h1>
            <p>System reports will be displayed here.</p>
        </div>
    );
}''',

    'Settings.tsx': '''import React from 'react';

export default function Settings() {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Settings</h1>
            <p>Application settings go here.</p>
        </div>
    );
}'''
}

for name, content in pages.items():
    v = os.path.join(pages_dir, name)
    with open(v, 'w') as f:
        f.write(content)

app_tsx = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Students from './pages/Students';
import Classes from './pages/Classes';
import Sessions from './pages/Sessions';
import LiveCamera from './pages/LiveCamera';
import Attendance from './pages/Attendance';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { token } = useAuth();
  
  if (!token) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/students" element={<ProtectedRoute><Students /></ProtectedRoute>} />
          <Route path="/classes" element={<ProtectedRoute><Classes /></ProtectedRoute>} />
          <Route path="/sessions" element={<ProtectedRoute><Sessions /></ProtectedRoute>} />
          <Route path="/live-camera" element={<ProtectedRoute><LiveCamera /></ProtectedRoute>} />
          <Route path="/attendance" element={<ProtectedRoute><Attendance /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
'''
with open('frontend/src/App.tsx', 'w') as f:
    f.write(app_tsx)

print("Pages created successfully.")
