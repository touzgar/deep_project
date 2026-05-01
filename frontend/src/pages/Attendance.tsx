import React, { useState, useEffect } from 'react';
import { Download, Filter, Calendar, Clock, FileText, BookOpen } from 'lucide-react';
import api from '../services/api';

interface AttendanceRecord {
  id: number;
  session_id: number;
  student_id: number;
  student_name: string;
  status: string;
  confidence: number | null;
  check_in_time: string;
}

interface Session {
  id: number;
  title: string;
  date: string;
  class_id: number;
}

interface Class {
  id: number;
  name: string;
}

export default function Attendance() {
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filteredSession, setFilteredSession] = useState('');
  const [filteredClass, setFilteredClass] = useState('');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchAttendance();
    fetchClasses();
    fetchSessions();
  }, []);

  useEffect(() => {
    // When class changes, fetch sessions for that class
    if (filteredClass) {
      fetchSessions(parseInt(filteredClass));
      setFilteredSession(''); // Reset session filter
    } else {
      fetchSessions();
    }
  }, [filteredClass]);

  const fetchAttendance = async () => {
    try {
      const { data } = await api.get('/attendance/');
      console.log('Attendance data:', data);
      setAttendanceRecords(data);
    } catch (e) { 
      console.error('Error fetching attendance:', e); 
    } finally { 
      setLoading(false); 
    }
  };

  const fetchClasses = async () => {
    try {
      const { data } = await api.get('/classes/');
      console.log('Classes data:', data);
      setClasses(data);
    } catch (e) { 
      console.error('Error fetching classes:', e); 
    }
  };

  const fetchSessions = async (classId?: number) => {
    try {
      const url = classId ? `/reports/sessions?class_id=${classId}` : '/reports/sessions';
      const { data } = await api.get(url);
      console.log('Sessions data:', data);
      setSessions(data);
    } catch (e) { 
      console.error('Error fetching sessions:', e); 
    }
  };

  const handleExport = async (format: 'excel' | 'pdf') => {
    setExporting(true);
    try {
      const endpoint = format === 'excel' 
        ? '/reports/attendance/export-excel' 
        : '/reports/attendance/export-pdf';
      
      // Build query params based on filters
      const params = new URLSearchParams();
      if (filteredSession) {
        params.append('session_id', filteredSession);
      }
      if (filteredClass) {
        params.append('class_id', filteredClass);
      }
      
      const queryString = params.toString();
      const url = queryString ? `${endpoint}?${queryString}` : endpoint;
      
      const { data } = await api.get(url, { 
        responseType: 'blob' 
      });
      
      const blob = new Blob([data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      const extension = format === 'excel' ? 'xlsx' : 'pdf';
      const filename = `attendance_${new Date().toISOString().split('T')[0]}.${extension}`;
      link.setAttribute('download', filename);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (e) { 
      console.error('Error exporting:', e);
      alert(`Failed to export ${format.toUpperCase()}. Please try again.`);
    } finally {
      setExporting(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Invalid Date';
      }
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      console.error('Date formatting error:', e);
      return 'Invalid Date';
    }
  };

  const formatTime = (dateString: string) => {
    try {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Invalid Time';
      }
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (e) {
      console.error('Time formatting error:', e);
      return 'Invalid Time';
    }
  };

  // Get session info for a record
  const getSessionInfo = (sessionId: number) => {
    const session = sessions.find(s => s.id === sessionId);
    return session ? session.title : `Session #${sessionId}`;
  };

  // Filter records
  const filtered = attendanceRecords.filter(record => {
    if (filteredSession && record.session_id.toString() !== filteredSession) {
      return false;
    }
    if (filteredClass) {
      const session = sessions.find(s => s.id === record.session_id);
      if (!session || session.class_id.toString() !== filteredClass) {
        return false;
      }
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Modern Header */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">📋 Attendance History</h1>
            <p className="text-green-100">View and export attendance records with advanced filters</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => handleExport('excel')} 
              disabled={attendanceRecords.length === 0 || exporting}
              className="bg-white text-green-600 px-5 py-3 rounded-xl flex items-center gap-2 hover:bg-green-50 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-105 shadow-lg font-semibold"
            >
              <Download className="w-5 h-5"/> 
              {exporting ? 'Exporting...' : 'Excel'}
            </button>
            <button 
              onClick={() => handleExport('pdf')} 
              disabled={attendanceRecords.length === 0 || exporting}
              className="bg-white text-red-600 px-5 py-3 rounded-xl flex items-center gap-2 hover:bg-red-50 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-105 shadow-lg font-semibold"
            >
              <FileText className="w-5 h-5"/> 
              {exporting ? 'Exporting...' : 'PDF'}
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-xl p-6">
        <div className="flex items-center gap-2 mb-6">
          <div className="bg-gradient-to-r from-blue-500 to-indigo-500 p-2 rounded-lg">
            <Filter className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">Smart Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Class Filter */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-600" />
              Filter by Class
            </label>
            <select 
              value={filteredClass} 
              onChange={(e) => setFilteredClass(e.target.value)} 
              className="w-full border-2 border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            >
              <option value="">All Classes</option>
              {classes.map((cls) => (
                <option key={cls.id} value={cls.id}>{cls.name}</option>
              ))}
            </select>
          </div>

          {/* Session Filter */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-600" />
              Filter by Session
            </label>
            <select 
              value={filteredSession} 
              onChange={(e) => setFilteredSession(e.target.value)} 
              className="w-full border-2 border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              disabled={sessions.length === 0}
            >
              <option value="">All Sessions</option>
              {sessions.map((session) => (
                <option key={session.id} value={session.id}>
                  {session.title} - {formatDate(session.date)}
                </option>
              ))}
            </select>
            {sessions.length === 0 && (
              <p className="text-xs text-gray-500 mt-2 italic">No sessions available</p>
            )}
          </div>
        </div>

        {/* Active Filters Display */}
        {(filteredClass || filteredSession) && (
          <div className="mt-6 flex items-center gap-3 flex-wrap">
            <span className="text-sm font-semibold text-gray-600">Active filters:</span>
            {filteredClass && (
              <span className="bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800 px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2">
                <BookOpen className="w-3 h-3" />
                {classes.find(c => c.id.toString() === filteredClass)?.name}
              </span>
            )}
            {filteredSession && (
              <span className="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2">
                <Calendar className="w-3 h-3" />
                {getSessionInfo(parseInt(filteredSession))}
              </span>
            )}
            <button
              onClick={() => {
                setFilteredClass('');
                setFilteredSession('');
              }}
              className="text-red-600 hover:text-red-800 underline text-sm font-semibold ml-2 hover:bg-red-50 px-3 py-1 rounded-lg transition-all"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">
            Attendance Records ({filtered.length} {filtered.length === 1 ? 'record' : 'records'})
          </h2>
        </div>

        {filtered.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="font-medium">No attendance records found</p>
            <p className="text-sm mt-1">
              {attendanceRecords.length === 0 
                ? 'Start taking attendance to see records here' 
                : 'Try adjusting your filters'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Session
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Time In
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filtered.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {record.student_name || `Student #${record.student_id}`}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">
                        {getSessionInfo(record.session_id)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                        {formatDate(record.check_in_time)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="w-4 h-4 mr-2 text-gray-400" />
                        {formatTime(record.check_in_time)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">
                        {record.confidence !== null 
                          ? `${(record.confidence * 100).toFixed(1)}%` 
                          : 'Manual'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        record.status === 'Present' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {record.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
