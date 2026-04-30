import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, BookOpen } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Teacher {
  id: number;
  username: string;
  email: string;
}

export default function Classes() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ 
    name: '', 
    description: '', 
    teacher_id: 0 
  });

  useEffect(() => { 
    fetchClasses();
    if (isAdmin) {
      fetchTeachers();
    }
  }, [isAdmin]);

  const fetchClasses = async () => {
    try {
      const { data } = await api.get('/classes/');
      setClasses(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const fetchTeachers = async () => {
    try {
      // Fetch all users and filter teachers (or create a dedicated endpoint)
      const { data } = await api.get('/auth/users');
      setTeachers(data.filter((u: any) => u.role === 'teacher' || u.role === 'admin'));
    } catch (e) { 
      console.error('Could not fetch teachers:', e);
      setTeachers([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/classes/${editingId}`, formData);
      } else {
        await api.post('/classes/', formData);
      }
      setShowModal(false); fetchClasses();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this class?')) {
      try {
        await api.delete(`/classes/${id}`);
        fetchClasses();
      } catch (e) { console.error(e); }
    }
  };

  const openModal = (cls: any = null) => {
    if (cls) { 
      setEditingId(cls.id); 
      setFormData({ 
        name: cls.name, 
        description: cls.description || '',
        teacher_id: cls.teacher_id || 0
      }); 
    } else { 
      setEditingId(null); 
      setFormData({ 
        name: '', 
        description: '',
        teacher_id: teachers.length > 0 ? teachers[0].id : 0
      }); 
    }
    setShowModal(true);
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      {/* Modern Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {isAdmin ? '📚 Classes Management' : '📚 My Classes'}
            </h1>
            <p className="text-purple-100">
              {isAdmin 
                ? 'Manage all classes and assign teachers' 
                : 'View your assigned classes and their details'}
            </p>
          </div>
          {isAdmin && (
            <button 
              onClick={() => openModal()} 
              className="bg-white text-purple-600 px-6 py-3 rounded-xl flex items-center gap-2 hover:bg-purple-50 transition-all transform hover:scale-105 shadow-lg font-semibold"
            >
              <Plus className="w-5 h-5"/> Add Class
            </button>
          )}
        </div>
      </div>

      {/* Classes Grid */}
      {classes.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-xl p-16 text-center">
          <BookOpen className="w-24 h-24 text-gray-300 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-700 mb-2">No Classes Yet</h3>
          <p className="text-gray-500">
            {isAdmin ? 'Create your first class to get started' : 'No classes assigned to you yet'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes.map((cls: any) => (
            <div 
              key={cls.id} 
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden group"
            >
              {/* Card Header with Gradient */}
              <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2">{cls.name}</h3>
                    <p className="text-purple-100 text-sm line-clamp-2">
                      {cls.description || 'No description provided'}
                    </p>
                  </div>
                  <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
                    <BookOpen className="w-6 h-6" />
                  </div>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-6">
                {/* Teacher Info */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Assigned Teacher</p>
                  {cls.teacher_name ? (
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {cls.teacher_name.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium text-gray-900">{cls.teacher_name}</span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400 italic">Not assigned</span>
                  )}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-purple-50 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-purple-600">0</p>
                    <p className="text-xs text-purple-700 font-medium">Students</p>
                  </div>
                  <div className="bg-pink-50 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-pink-600">0</p>
                    <p className="text-xs text-pink-700 font-medium">Sessions</p>
                  </div>
                </div>

                {/* Actions */}
                {isAdmin && (
                  <div className="flex gap-2">
                    <button 
                      onClick={() => openModal(cls)} 
                      className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all flex items-center justify-center gap-2 font-semibold"
                    >
                      <Edit2 className="w-4 h-4"/>
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDelete(cls.id)} 
                      className="bg-red-50 text-red-600 px-4 py-2 rounded-lg hover:bg-red-100 transition-all flex items-center justify-center"
                    >
                      <Trash2 className="w-4 h-4"/>
                    </button>
                  </div>
                )}
              </div>

              {/* Card Footer */}
              <div className="bg-gray-50 px-6 py-3 border-t border-gray-100">
                <p className="text-xs text-gray-500">
                  Class ID: <span className="font-mono font-semibold text-gray-700">#{cls.id}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal remains the same */}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">{editingId ? 'Edit Class' : 'Add Class'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class Name *</label>
                <input 
                  required 
                  type="text" 
                  value={formData.name} 
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
                  placeholder="e.g., Computer Science 101" 
                  className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea 
                  value={formData.description} 
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
                  placeholder="Brief description of the class" 
                  rows={3}
                  className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              {isAdmin && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Assign Teacher</label>
                  <select
                    value={formData.teacher_id}
                    onChange={(e) => setFormData({ ...formData, teacher_id: parseInt(e.target.value) })}
                    className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value={0}>No teacher assigned</option>
                    {teachers.map((teacher) => (
                      <option key={teacher.id} value={teacher.id}>
                        {teacher.username} ({teacher.email})
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    The assigned teacher will see this class and its students
                  </p>
                </div>
              )}
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => setShowModal(false)} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Cancel</button>
                <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}