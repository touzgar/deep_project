import React, { useState, useEffect } from 'react';
import { Save, LogOut, User, Mail, Shield, Calendar, BookOpen, Users, Award, TrendingUp, Clock } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';
  
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalStudents: 0,
    totalClasses: 0,
    attendanceRate: 0
  });
  const [recentSessions, setRecentSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      // Fetch dashboard stats (already filtered by role)
      const { data: dashboardData } = await api.get('/dashboard/stats');
      setStats({
        totalSessions: dashboardData.totalSessions || 0,
        totalStudents: dashboardData.totalStudents || 0,
        totalClasses: dashboardData.totalClasses || 0,
        attendanceRate: dashboardData.attendancePercentage || 0
      });

      // Fetch recent sessions (already filtered by role)
      const { data: sessionsData } = await api.get('/sessions/?limit=5');
      setRecentSessions(sessionsData);
    } catch (e) {
      console.error('Error fetching profile data:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg">
              <span className="text-4xl font-bold text-indigo-600">
                {user?.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h1 className="text-3xl font-bold">{user?.username}</h1>
              <p className="text-indigo-100 flex items-center gap-2 mt-1">
                <Mail className="w-4 h-4" />
                {user?.email}
              </p>
              <div className="mt-2 inline-flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                <Shield className="w-4 h-4" />
                <span className="font-semibold capitalize">{user?.role}</span>
              </div>
            </div>
          </div>
          <button
            onClick={logout}
            className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-all"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">
                {isAdmin ? 'Total Sessions' : 'My Sessions'}
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalSessions}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">
                {isAdmin ? 'Total Students' : 'My Students'}
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalStudents}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Users className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">
                {isAdmin ? 'Total Classes' : 'My Classes'}
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalClasses}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <BookOpen className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Attendance Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.attendanceRate.toFixed(1)}%</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-full">
              <TrendingUp className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Sessions */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-600" />
            {isAdmin ? 'Recent Sessions' : 'My Recent Sessions'}
          </h2>
          {recentSessions.length > 0 ? (
            <div className="space-y-3">
              {recentSessions.map((session) => (
                <div
                  key={session.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{session.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Class: {session.class_name || `Class ${session.class_id}`}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(session.start_time).toLocaleDateString()} at{' '}
                        {new Date(session.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          session.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : session.status === 'completed'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {session.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Calendar className="w-16 h-16 mx-auto text-gray-300 mb-3" />
              <p>No sessions yet</p>
              <p className="text-sm mt-1">Create your first session to get started!</p>
            </div>
          )}
        </div>

        {/* Profile Info & Actions */}
        <div className="space-y-6">
          {/* Account Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-indigo-600" />
              Account Info
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Username</label>
                <p className="text-gray-900 font-medium mt-1">{user?.username}</p>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Email</label>
                <p className="text-gray-900 font-medium mt-1">{user?.email}</p>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Role</label>
                <p className="text-gray-900 font-medium mt-1 capitalize">{user?.role}</p>
              </div>
              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Status</label>
                <div className="flex items-center gap-2 mt-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-900 font-medium">Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <a
                href="/sessions"
                className="block w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-4 py-3 rounded-lg text-center font-medium transition-colors"
              >
                Create New Session
              </a>
              <a
                href="/live-camera"
                className="block w-full bg-green-50 hover:bg-green-100 text-green-700 px-4 py-3 rounded-lg text-center font-medium transition-colors"
              >
                Take Attendance
              </a>
              <a
                href="/reports"
                className="block w-full bg-purple-50 hover:bg-purple-100 text-purple-700 px-4 py-3 rounded-lg text-center font-medium transition-colors"
              >
                View Reports
              </a>
            </div>
          </div>

          {/* Performance Badge */}
          {stats.attendanceRate >= 90 && (
            <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg shadow-md p-6 text-white">
              <div className="flex items-center gap-3">
                <Award className="w-12 h-12" />
                <div>
                  <h3 className="font-bold text-lg">Excellent!</h3>
                  <p className="text-sm text-white/90">
                    {stats.attendanceRate.toFixed(0)}% attendance rate
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}