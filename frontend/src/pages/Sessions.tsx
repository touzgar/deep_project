import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Session {
  id: number;
  title: string;
  class_id: number;
  teacher_id: number;
  start_time: string;
  end_time: string;
  status: string;
  class_name?: string;
  teacher_name?: string;
}

interface Class {
  id: number;
  name: string;
}

export default function Sessions() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ 
    title: '', 
    class_id: 0,
    start_time: '',
    end_time: '',
    status: 'scheduled'
  });

  useEffect(() => { 
    fetchSessions();
    fetchClasses();
  }, []);

  const fetchSessions = async () => {
    try {
      const { data } = await api.get('/sessions/');
      setSessions(data);
    } catch (e) { 
      console.error(e); 
    } finally { 
      setLoading(false); 
    }
  };

  const fetchClasses = async () => {
    try {
      const { data } = await api.get('/classes/');
      setClasses(data);
      if (data.length > 0 && formData.class_id === 0) {
        setFormData(prev => ({ ...prev, class_id: data[0].id }));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        teacher_id: user?.id || 1,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString()
      };

      if (editingId) {
        await api.put(`/sessions/${editingId}`, payload);
      } else {
        await api.post('/sessions/', payload);
      }
      setShowModal(false); 
      fetchSessions();
      resetForm();
    } catch (e: any) { 
      alert(e.response?.data?.detail || 'Error saving session');
      console.error(e); 
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Delete this session?')) {
      try {
        await api.delete(`/sessions/${id}`);
        fetchSessions();
      } catch (e) { 
        console.error(e); 
      }
    }
  };

  const resetForm = () => {
    setFormData({ 
      title: '', 
      class_id: classes.length > 0 ? classes[0].id : 0,
      start_time: '',
      end_time: '',
      status: 'scheduled'
    });
    setEditingId(null);
  };

  const openModal = (session: Session | null = null) => {
    if (session) { 
      setEditingId(session.id); 
      setFormData({ 
        title: session.title,
        class_id: session.class_id,
        start_time: session.start_time.slice(0, 16),
        end_time: session.end_time.slice(0, 16),
        status: session.status
      }); 
    } else { 
      resetForm();
    }
    setShowModal(true);
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Sessions Management</h1>
        <button 
          onClick={() => openModal()} 
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700"
        >
          <Plus className="w-4 h-4"/> Add Session
        </button>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Title</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Class</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Teacher</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Start Time</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Status</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sessions.map((session) => (
              <tr key={session.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">{session.title}</td>
                <td className="px-6 py-4">{session.class_name || `Class ${session.class_id}`}</td>
                <td className="px-6 py-4">{session.teacher_name || `Teacher ${session.teacher_id}`}</td>
                <td className="px-6 py-4">{new Date(session.start_time).toLocaleString()}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    session.status === 'completed' ? 'bg-green-100 text-green-800' :
                    session.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {session.status}
                  </span>
                </td>
                <td className="px-6 py-4 flex gap-2">
                  <button 
                    onClick={() => openModal(session)} 
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    <Edit2 className="w-4 h-4"/>
                  </button>
                  <button 
                    onClick={() => handleDelete(session.id)} 
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4"/>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">{editingId ? 'Edit Session' : 'Add Session'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input 
                  required 
                  type="text" 
                  value={formData.title} 
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })} 
                  placeholder="Session Title" 
                  className="w-full border border-gray-300 p-2 rounded" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class *</label>
                <select
                  required
                  value={formData.class_id}
                  onChange={(e) => setFormData({ ...formData, class_id: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 p-2 rounded"
                >
                  <option value={0} disabled>Select a class</option>
                  {classes.map((cls) => (
                    <option key={cls.id} value={cls.id}>
                      {cls.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Time *</label>
                <input 
                  required 
                  type="datetime-local" 
                  value={formData.start_time} 
                  onChange={(e) => setFormData({ ...formData, start_time: e.target.value })} 
                  className="w-full border border-gray-300 p-2 rounded" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Time *</label>
                <input 
                  required 
                  type="datetime-local" 
                  value={formData.end_time} 
                  onChange={(e) => setFormData({ ...formData, end_time: e.target.value })} 
                  className="w-full border border-gray-300 p-2 rounded" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full border border-gray-300 p-2 rounded"
                >
                  <option value="scheduled">Scheduled</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div className="flex justify-end gap-2">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)} 
                  className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
