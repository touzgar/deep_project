import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function Sessions() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', class_id: '' });

  useEffect(() => { fetchSessions(); }, []);

  const fetchSessions = async () => {
    try {
      const { data } = await api.get('/sessions/');
      setSessions(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/sessions/${editingId}`, formData);
      } else {
        await api.post('/sessions/', formData);
      }
      setShowModal(false); fetchSessions();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this session?')) {
      try {
        await api.delete(`/sessions/${id}`);
        fetchSessions();
      } catch (e) { console.error(e); }
    }
  };

  const openModal = (session: any = null) => {
    if (session) { 
      setEditingId(session.id); 
      setFormData({ name: session.name, description: session.description || '', class_id: session.class_id || '' }); 
    } else { 
      setEditingId(null); 
      setFormData({ name: '', description: '', class_id: '' }); 
    }
    setShowModal(true);
  };

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Sessions Management</h1>
        <button onClick={() => openModal()} className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700">
          <Plus className="w-4 h-4"/> Add Session
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
            {sessions.map((session: any) => (
              <tr key={session.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">{session.name}</td>
                <td className="px-6 py-4">{session.description}</td>
                <td className="px-6 py-4 flex gap-2">
                  <button onClick={() => openModal(session)} className="text-indigo-600 hover:text-indigo-900"><Edit2 className="w-4 h-4"/></button>
                  <button onClick={() => handleDelete(session.id)} className="text-red-600 hover:text-red-900"><Trash2 className="w-4 h-4"/></button>
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
              <input required type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="Session Name" className="w-full border border-gray-300 p-2 rounded" />
              <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} placeholder="Description" className="w-full border border-gray-300 p-2 rounded" />
              <input type="text" value={formData.class_id} onChange={(e) => setFormData({ ...formData, class_id: e.target.value })} placeholder="Class ID" className="w-full border border-gray-300 p-2 rounded" />
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