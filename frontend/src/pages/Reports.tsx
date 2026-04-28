import React, { useState, useEffect } from 'react';
import { Download, TrendingUp } from 'lucide-react';
import api from '../services/api';

export default function Reports() {
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [reportType, setReportType] = useState('summary');

  useEffect(() => {
    fetchReport();
  }, [reportType]);

  const fetchReport = async () => {
    try {
      const { data } = await api.get(`/reports/${reportType}`);
      setReportData(data);
    } catch (e) {
      console.error('Error fetching report:', e);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (format: 'pdf' | 'excel') => {
    try {
      const { data } = await api.get(`/reports/${reportType}/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
    } catch (e) {
      console.error('Error exporting report:', e);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reports</h1>
        <div className="flex gap-2">
          <button onClick={() => exportReport('pdf')} className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-red-700">
            <Download className="w-4 h-4"/> PDF
          </button>
          <button onClick={() => exportReport('excel')} className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700">
            <Download className="w-4 h-4"/> Excel
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-4">
        <div className="mb-6 flex gap-4">
          <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="border border-gray-300 p-2 rounded">
            <option value="summary">Summary Report</option>
            <option value="attendance">Attendance Report</option>
            <option value="class-wise">Class-Wise Report</option>
            <option value="student-wise">Student-Wise Report</option>
          </select>
        </div>

        {reportData && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {reportData.stats && Object.entries(reportData.stats).map(([key, value]: any) => (
                <div key={key} className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                  <div className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                  <div className="text-2xl font-bold text-blue-600">{value}</div>
                </div>
              ))}
            </div>

            {reportData.data && (
              <div className="mt-6 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(reportData.data[0] || {}).map((key) => (
                        <th key={key} className="px-6 py-3 text-left text-xs font-semibold text-gray-600">{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {reportData.data.map((row: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((cell: any, cellIdx: number) => (
                          <td key={cellIdx} className="px-6 py-4 text-sm text-gray-900">{String(cell)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}