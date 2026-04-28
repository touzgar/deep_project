import React, { useState, useEffect } from 'react';
import { Download, Filter } from 'lucide-react';
import api from '../services/api';

export default function Attendance() {
  const [attendanceRecords, setAttendanceRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filteredClass, setFilteredClass] = useState('');
  const [classes, setClasses] = useState<any[]>([]);

  useEffect(() => {
    fetchAttendance();
    fetchClasses();
  }, []);

  const fetchAttendance = async () => {
    try {
      const { data } = await api.get('/attendance/');
      setAttendanceRecords(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const fetchClasses = async () => {
    try {
      const { data } = await api.get('/classes/');
      setClasses(data);
    } catch (e) { console.error(e); }
  };

  const handleExport = async () => {
    try {
      const { data } = await api.get('/attendance/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'attendance.csv');
      document.body.appendChild(link);
      link.click();
    } catch (e) { console.error(e); }
  };

  const filtered = filteredClass ? attendanceRecords.filter(r => r.class_id === filteredClass) : attendanceRecords;

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Attendance History</h1>
        <button onClick={handleExport} className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700">
          <Download className="w-4 h-4"/> Export CSV
        </button>
      </div>

      <div className="bg-white shadow rounded-lg p-4">
        <div className="mb-4 flex gap-4">
          <select value={filteredClass} onChange={(e) => setFilteredClass(e.target.value)} className="border border-gray-300 p-2 rounded">
            <option value="">All Classes</option>
            {classes.map((cls: any) => (
              <option key={cls.id} value={cls.id}>{cls.name}</option>
            ))}
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Student</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Time In</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filtered.map((record: any) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{record.student_name || record.student_id}</td>
                  <td className="px-6 py-4">{new Date(record.timestamp).toLocaleDateString()}</td>
                  <td className="px-6 py-4">{new Date(record.timestamp).toLocaleTimeString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-white text-sm ${record.status === 'present' ? 'bg-green-600' : 'bg-red-600'}`}>
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
