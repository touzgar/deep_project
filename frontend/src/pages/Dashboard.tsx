import { useEffect, useState } from 'react';
import { Users, UserCheck, UserX, BookOpen, Calendar, Activity, TrendingUp, Award, Target, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalClasses: 0,
    totalSessionsToday: 0,
    presentToday: 0,
    absentToday: 0,
    attendancePercentage: 0,
    weeklyAttendance: [],
    monthlyAttendanceRate: [],
    presentVsAbsent: []
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/dashboard/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600 font-medium">Loading your dashboard...</p>
      </div>
    </div>
  );

  const statCards = [
    { 
      name: isAdmin ? 'Total Students' : 'My Students', 
      value: stats.totalStudents, 
      icon: Users, 
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      iconBg: 'bg-blue-500',
      change: '+12%',
      changePositive: true
    },
    { 
      name: isAdmin ? 'Total Classes' : 'My Classes', 
      value: stats.totalClasses, 
      icon: BookOpen, 
      gradient: 'from-indigo-500 to-indigo-600',
      bgGradient: 'from-indigo-50 to-indigo-100',
      iconBg: 'bg-indigo-500',
      change: '+5%',
      changePositive: true
    },
    { 
      name: 'Sessions Today', 
      value: stats.totalSessionsToday, 
      icon: Calendar, 
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100',
      iconBg: 'bg-purple-500',
      change: '3 active',
      changePositive: true
    },
    { 
      name: 'Present Today', 
      value: stats.presentToday, 
      icon: UserCheck, 
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100',
      iconBg: 'bg-green-500',
      change: '+8%',
      changePositive: true
    },
    { 
      name: 'Absent Today', 
      value: stats.absentToday, 
      icon: UserX, 
      gradient: 'from-red-500 to-red-600',
      bgGradient: 'from-red-50 to-red-100',
      iconBg: 'bg-red-500',
      change: '-3%',
      changePositive: true
    },
    { 
      name: 'Attendance Rate', 
      value: `${stats.attendancePercentage}%`, 
      icon: Activity, 
      gradient: 'from-teal-500 to-teal-600',
      bgGradient: 'from-teal-50 to-teal-100',
      iconBg: 'bg-teal-500',
      change: '+2.5%',
      changePositive: true
    },
  ];

  const pieColors = ['#22c55e', '#ef4444', '#eab308'];

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Welcome back, {user?.username}! 👋
            </h1>
            <p className="text-indigo-100 text-lg">
              {isAdmin ? "Here's your complete system overview" : "Here's your teaching dashboard"}
            </p>
          </div>
          <div className="hidden md:flex items-center gap-4">
            {stats.attendancePercentage >= 90 && (
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
                <Award className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm font-semibold">Excellent!</p>
                <p className="text-xs text-indigo-100">High attendance</p>
              </div>
            )}
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
              <Zap className="w-12 h-12 mx-auto mb-2" />
              <p className="text-sm font-semibold">{stats.totalSessionsToday}</p>
              <p className="text-xs text-indigo-100">Active Sessions</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Modern Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {statCards.map((item, index) => (
          <div 
            key={item.name} 
            className={`bg-gradient-to-br ${item.bgGradient} rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${item.iconBg} shadow-lg`}>
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                {item.change && (
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                    item.changePositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {item.change}
                  </span>
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{item.name}</p>
                <p className="text-3xl font-bold text-gray-900">{item.value}</p>
              </div>
            </div>
            <div className={`h-1 bg-gradient-to-r ${item.gradient}`}></div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Weekly Attendance Chart */}
        <div className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <div className="w-2 h-8 bg-gradient-to-b from-green-500 to-red-500 rounded-full"></div>
              Weekly Attendance
            </h2>
            <div className="bg-gradient-to-r from-green-100 to-red-100 px-3 py-1 rounded-full">
              <span className="text-xs font-semibold text-gray-700">Last 7 Days</span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.weeklyAttendance}>
                <defs>
                  <linearGradient id="colorPresent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0.3}/>
                  </linearGradient>
                  <linearGradient id="colorAbsent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: '12px' }} />
                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: 'none', 
                    borderRadius: '12px', 
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)' 
                  }} 
                />
                <Legend wrapperStyle={{ fontSize: '14px', fontWeight: '600' }} />
                <Bar dataKey="present" fill="url(#colorPresent)" name="Present" radius={[8, 8, 0, 0]} />
                <Bar dataKey="absent" fill="url(#colorAbsent)" name="Absent" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Rate Chart */}
        <div className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <div className="w-2 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
              Attendance Trend
            </h2>
            <div className="bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 rounded-full">
              <span className="text-xs font-semibold text-gray-700">Monthly %</span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.monthlyAttendanceRate}>
                <defs>
                  <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: '12px' }} />
                <YAxis domain={[0, 100]} stroke="#6b7280" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: 'none', 
                    borderRadius: '12px', 
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)' 
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="rate" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  fill="url(#colorRate)" 
                  name="Attendance %" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Today's Overview */}
        <div className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <div className="w-2 h-8 bg-gradient-to-b from-green-500 to-yellow-500 rounded-full"></div>
              Today's Overview
            </h2>
            <div className="bg-gradient-to-r from-green-100 to-yellow-100 px-3 py-1 rounded-full">
              <span className="text-xs font-semibold text-gray-700">Live</span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <defs>
                  <filter id="shadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                <Pie
                  data={stats.presentVsAbsent}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  labelLine={false}
                  style={{ filter: 'url(#shadow)' }}
                >
                  {stats.presentVsAbsent.map((entry: any, index: number) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={pieColors[index % pieColors.length]}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: 'none', 
                    borderRadius: '12px', 
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)' 
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="bg-green-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.presentToday}</p>
              <p className="text-xs text-green-700 font-medium">Present</p>
            </div>
            <div className="bg-red-50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-600">{stats.absentToday}</p>
              <p className="text-xs text-red-700 font-medium">Absent</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions for Teachers */}
      {!isAdmin && (
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl shadow-xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Target className="w-7 h-7" />
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/sessions"
              className="bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl p-6 transition-all transform hover:scale-105"
            >
              <Calendar className="w-10 h-10 mb-3" />
              <h3 className="font-bold text-lg mb-1">Create Session</h3>
              <p className="text-sm text-purple-100">Start a new class session</p>
            </a>
            <a
              href="/live-camera"
              className="bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl p-6 transition-all transform hover:scale-105"
            >
              <UserCheck className="w-10 h-10 mb-3" />
              <h3 className="font-bold text-lg mb-1">Take Attendance</h3>
              <p className="text-sm text-purple-100">Use AI face recognition</p>
            </a>
            <a
              href="/reports"
              className="bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl p-6 transition-all transform hover:scale-105"
            >
              <TrendingUp className="w-10 h-10 mb-3" />
              <h3 className="font-bold text-lg mb-1">View Reports</h3>
              <p className="text-sm text-purple-100">Analyze attendance data</p>
            </a>
          </div>
        </div>
      )}
    </div>
  );
}