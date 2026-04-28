import os

students_content = """import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function Students() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ first_name: '', last_name: '', student_id: '' });

  useEffect(() => { fetchStudents(); }, []);

  const fetchStudents = async () => {
    try {
      const { data } = await api.get('/students/');
      setStudents(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/students/${editingId}`, formData);
      } else {
        await api.post('/students/', formData);
      }
      setShowModal(false); fetchStudents();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete?')) {
      await api.delete(`/students/${id}`); fetchStudents();
    }
  };

  const openModal = (student: any = null) => {
    if (student) { 
        setEditingId(student.id); 
        setFormData({student_id: student.student_id, first_name: student.first_name, last_name: student.last_name}); 
    } else { 
        setEditingId(null); 
        setFormData({ first_name: '', last_name: '', student_id: '' }); 
    }
    setShowModal(true);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Students</h1>
        <button onClick={() => openModal()} className="bg-indigo-600 text-white px-4 py-2 rounded flex"><Plus/> Add</button>
      </div>
      <div className="bg-white shadow rounded p-4">
        <table className="min-w-full">
          <thead><tr><th>ID</th><th>First Name</th><th>Last Name</th><th>Actions</th></tr></thead>
          <tbody>
            {students.map((s: any) => (
              <tr key={s.id}>
                <td>{s.student_id}</td><td>{s.first_name}</td><td>{s.last_name}</td>
                <td>
                  <button onClick={() => openModal(s)}><Edit2 className="w-4 h-4"/></button>
                  <button onClick={() => handleDelete(s.id)}><Trash2 className="w-4 h-4"/></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded w-full max-w-md">
             <h2 className="text-xl mb-4 text-center font-semibold">{editingId ? 'Edit' : 'Add'} Student</h2>
             <form onSubmit={handleSubmit} className="space-y-4">
               <input required value={formData.student_id} onChange={(e)=>setFormData({...formData, student_id: e.target.value})} placeholder="ID" className="w-full border p-2"/>
               <input required value={formData.first_name} onChange={(e)=>setFormData({...formData, first_name: e.target.value})} placeholder="First Name" className="w-full border p-2"/>
               <input required value={formData.last_name} onChange={(e)=>setFormData({...formData, last_name: e.target.value})} placeholder="Last Name" className="w-full border p-2"/>
               <div className="flex justify-end gap-2 mt-4">
                 <button type="button" onClick={() => setShowModal(false)} className="bg-gray-300 px-4 py-2 rounded">Cancel</button>
                 <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded">Save</button>
               </div>
             </form>
          </div>
        </div>
      )}
    </div>
  );
}
"""

with open('frontend/src/pages/Students.tsx', 'w') as f:
    f.write(students_content)

print("Done")
