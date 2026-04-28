import React, { useState, useEffect } from 'react';
import { Save, LogOut } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const { logout } = useAuth();
  const [settings, setSettings] = useState({ system_name: '', email_notifications: false, max_face_matches: 3 });
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { data } = await api.get('/settings/');
      setSettings(data);
    } catch (e) {
      console.error('Error fetching settings:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await api.put('/settings/', settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error('Error saving settings:', e);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-bold mb-4">System Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">System Name</label>
                <input
                  type="text"
                  value={settings.system_name}
                  onChange={(e) => setSettings({ ...settings, system_name: e.target.value })}
                  className="w-full mt-1 border border-gray-300 p-2 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Max Face Matches</label>
                <input
                  type="number"
                  value={settings.max_face_matches}
                  onChange={(e) => setSettings({ ...settings, max_face_matches: parseInt(e.target.value) })}
                  className="w-full mt-1 border border-gray-300 p-2 rounded"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.email_notifications}
                  onChange={(e) => setSettings({ ...settings, email_notifications: e.target.checked })}
                  className="mr-2"
                />
                <label className="text-sm font-medium text-gray-700">Enable Email Notifications</label>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleSave}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700"
              >
                <Save className="w-4 h-4"/> Save Settings
              </button>
              {saved && <p className="text-green-600 mt-2">Settings saved successfully!</p>}
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4">Account</h2>
          <button
            onClick={logout}
            className="w-full bg-red-600 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-red-700"
          >
            <LogOut className="w-4 h-4"/> Logout
          </button>
        </div>
      </div>
    </div>
  );
}