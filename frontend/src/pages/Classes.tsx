import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function Classes() {
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  useEffect(() => { fetchClasses(); }, []);

  const fetchClasses = async () => {
    try {
      const { data } = await api.get('/classes/');
      setClasses(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
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
      setFormData({ name: cls.name, description: cls.description || '' }); 
    } else { 
      setEditingId(null); 
      setFormData({ name: '', description: '' }); 
    }
    setShowModal(true);
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Classes Management</h1>
        <button onClick={() => openModal()} className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700">
          <Plus className="w-4 h-4"/> Add Class
        </button>
      </div>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Name</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Description</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {classes.map((cls: any) => (
              <tr key={cls.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">{cls.name}</td>
                <td className="px-6 py-4">{cls.description}</td>
                <td className="px-6 py-4 flex gap-2">
                  <button onClick={() => openModal(cls)} className="text-indigo-600 hover:text-indigo-900"><Edit2 className="w-4 h-4"/></button>
                  <button onClick={() => handleDelete(cls.id)} className="text-red-600 hover:text-red-900"><Trash2 className="w-4 h-4"/></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">{editingId ? 'Edit Class' : 'Add Class'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input required type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Class Name" className="w-full border border-gray-300 p-2 rounded" />
              <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} placeholder="Description" className="w-full border border-gray-300 p-2 rounded" />
              <div className="flex justify-end gap-2">
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