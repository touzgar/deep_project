import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Camera, Upload, X, Users, BookOpen } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Student {
  id: number;
  student_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  class_id: number;
  class_name?: string;
}

interface Class {
  id: number;
  name: string;
}

interface FaceImage {
  id: number;
  image_path: string;
  uploadthing_key?: string;
  has_embedding: boolean;
  created_at: string;
}

export default function Students() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  
  const [students, setStudents] = useState<Student[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [formData, setFormData] = useState({ 
    first_name: '', 
    last_name: '', 
    email: '',
    class_id: 0
  });
  
  // Photo upload states
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [studentFaceImages, setStudentFaceImages] = useState<FaceImage[]>([]);

  useEffect(() => { 
    fetchStudents();
    fetchClasses();
  }, []);

  const fetchStudents = async () => {
    try {
      const { data } = await api.get('/students/');
      setStudents(data);
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
      if (editingId) {
        await api.put(`/students/${editingId}`, formData);
      } else {
        await api.post('/students/', formData);
      }
      setShowModal(false); 
      fetchStudents();
      resetForm();
    } catch (e: any) { 
      alert(e.response?.data?.detail || 'Error saving student');
      console.error(e); 
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Delete this student? This will also delete all their face images.')) {
      try {
        await api.delete(`/students/${id}`); 
        fetchStudents();
      } catch (e) {
        console.error(e);
      }
    }
  };

  const resetForm = () => {
    setFormData({ 
      first_name: '', 
      last_name: '', 
      email: '', 
      class_id: classes.length > 0 ? classes[0].id : 0 
    });
    setEditingId(null);
  };

  const openModal = (student: Student | null = null) => {
    if (student) { 
      setEditingId(student.id); 
      setFormData({
        first_name: student.first_name, 
        last_name: student.last_name,
        email: student.email,
        class_id: student.class_id
      }); 
    } else { 
      resetForm();
    }
    setShowModal(true);
  };

  // Photo upload functions
  const openPhotoModal = async (student: Student) => {
    setSelectedStudent(student);
    setShowPhotoModal(true);
    await fetchStudentFaceImages(student.id);
  };

  const fetchStudentFaceImages = async (studentId: number) => {
    try {
      const { data } = await api.get(`/students/${studentId}/face-images`);
      setStudentFaceImages(data.face_images || []);
    } catch (e) {
      console.error('Error fetching face images:', e);
      setStudentFaceImages([]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length !== files.length) {
      alert('Only image files are allowed');
    }
    
    setSelectedFiles(prev => [...prev, ...imageFiles]);
    
    imageFiles.forEach(file => {
      const url = URL.createObjectURL(file);
      setPreviewUrls(prev => [...prev, url]);
    });
  };

  const removeFile = (index: number) => {
    URL.revokeObjectURL(previewUrls[index]);
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => prev.filter((_, i) => i !== index));
  };

  const uploadPhotos = async () => {
    if (!selectedStudent || selectedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress('Preparing upload...');

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      setUploadProgress('Uploading and processing images...');
      
      const { data } = await api.post(
        `/students/${selectedStudent.id}/face-images`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setUploadProgress(`Upload complete! ${data.uploaded_count} images processed successfully.`);
      
      if (data.errors && data.errors.length > 0) {
        console.warn('Upload errors:', data.errors);
        alert(`Some files had issues: ${data.errors.join(', ')}`);
      }

      clearSelectedFiles();
      await fetchStudentFaceImages(selectedStudent.id);
      
      setTimeout(() => {
        setUploadProgress('');
      }, 3000);

    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadProgress('Upload failed. Please try again.');
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const clearSelectedFiles = () => {
    previewUrls.forEach(url => URL.revokeObjectURL(url));
    setSelectedFiles([]);
    setPreviewUrls([]);
  };

  const deleteFaceImage = async (imageId: number) => {
    if (!selectedStudent) return;
    
    if (confirm('Delete this face image?')) {
      try {
        await api.delete(`/students/${selectedStudent.id}/face-images/${imageId}`);
        await fetchStudentFaceImages(selectedStudent.id);
      } catch (error) {
        console.error('Error deleting face image:', error);
        alert('Failed to delete face image');
      }
    }
  };

  const closePhotoModal = () => {
    setShowPhotoModal(false);
    setSelectedStudent(null);
    clearSelectedFiles();
    setStudentFaceImages([]);
    setUploadProgress('');
  };

  if (loading) return <div className="p-4">Loading students...</div>;

  return (
    <div className="space-y-6">
      {/* Modern Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {isAdmin ? '👥 Students Management' : '👥 My Students'}
            </h1>
            <p className="text-blue-100">
              {isAdmin 
                ? 'Manage all students in the system' 
                : 'View and manage photos for students in your classes'}
            </p>
          </div>
          {isAdmin && (
            <button 
              onClick={() => openModal()} 
              className="bg-white text-indigo-600 px-6 py-3 rounded-xl flex items-center gap-2 hover:bg-blue-50 transition-all transform hover:scale-105 shadow-lg font-semibold"
            >
              <Plus className="w-5 h-5" /> Add Student
            </button>
          )}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Students</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{students.length}</p>
            </div>
            <div className="bg-blue-100 p-4 rounded-xl">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">With Face Data</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {students.filter(s => s.id).length}
              </p>
            </div>
            <div className="bg-green-100 p-4 rounded-xl">
              <Camera className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Classes</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{classes.length}</p>
            </div>
            <div className="bg-purple-100 p-4 rounded-xl">
              <BookOpen className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Students Grid/Table */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Student Directory</h2>
        </div>
        
        {students.length === 0 ? (
          <div className="text-center py-16">
            <Users className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">No students yet</p>
            <p className="text-gray-400 text-sm mt-2">Add your first student to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Student</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Class</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Face Images</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id} className="hover:bg-blue-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-12 w-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                          {student.first_name.charAt(0)}{student.last_name.charAt(0)}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-bold text-gray-900">
                            {student.first_name} {student.last_name}
                          </div>
                          {student.student_id && (
                            <div className="text-xs text-gray-500">ID: {student.student_id}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{student.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-indigo-100 text-indigo-800">
                        {student.class_name || `Class ${student.class_id}`}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => openPhotoModal(student)}
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-semibold hover:from-blue-600 hover:to-indigo-600 flex items-center gap-2 transition-all transform hover:scale-105 shadow-md"
                      >
                        <Camera className="w-4 h-4" />
                        Manage Photos
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {isAdmin && (
                        <div className="flex items-center gap-3">
                          <button 
                            onClick={() => openModal(student)}
                            className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 p-2 rounded-lg transition-all"
                            title="Edit Student"
                          >
                            <Edit2 className="w-5 h-5" />
                          </button>
                          <button 
                            onClick={() => handleDelete(student.id)}
                            className="text-red-600 hover:text-red-900 hover:bg-red-50 p-2 rounded-lg transition-all"
                            title="Delete Student"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Student Form Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl mb-4 font-semibold">
              {editingId ? 'Edit' : 'Add'} Student
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                <input 
                  required 
                  value={formData.first_name} 
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})} 
                  placeholder="First Name" 
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                <input 
                  required 
                  value={formData.last_name} 
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})} 
                  placeholder="Last Name" 
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input 
                  required 
                  type="email"
                  value={formData.email} 
                  onChange={(e) => setFormData({...formData, email: e.target.value})} 
                  placeholder="Email" 
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class *</label>
                <select
                  required
                  value={formData.class_id}
                  onChange={(e) => setFormData({...formData, class_id: parseInt(e.target.value)})}
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
              <div className="flex justify-end gap-2 mt-6">
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

      {/* Photo Upload Modal - keeping existing implementation */}
      {showPhotoModal && selectedStudent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">
                Face Photos - {selectedStudent.first_name} {selectedStudent.last_name}
              </h2>
              <button 
                onClick={closePhotoModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="mb-6 p-4 border-2 border-dashed border-gray-300 rounded-lg">
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-2">
                  <label htmlFor="photo-upload" className="cursor-pointer">
                    <span className="mt-2 block text-sm font-medium text-gray-900">
                      Upload multiple face photos
                    </span>
                    <span className="mt-1 block text-xs text-gray-500">
                      PNG, JPG, GIF up to 10MB each
                    </span>
                  </label>
                  <input
                    id="photo-upload"
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
              </div>
            </div>

            {selectedFiles.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3">Selected Photos ({selectedFiles.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {previewUrls.map((url, index) => (
                    <div key={index} className="relative">
                      <img 
                        src={url} 
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg border"
                      />
                      <button
                        onClick={() => removeFile(index)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                      <div className="mt-1 text-xs text-gray-500 truncate">
                        {selectedFiles[index].name}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={uploadPhotos}
                    disabled={uploading}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    {uploading ? 'Processing...' : `Upload ${selectedFiles.length} Photos`}
                  </button>
                  <button
                    onClick={clearSelectedFiles}
                    className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                  >
                    Clear All
                  </button>
                </div>

                {uploadProgress && (
                  <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
                    {uploadProgress}
                  </div>
                )}
              </div>
            )}

            <div>
              <h3 className="text-lg font-medium mb-3">
                Existing Face Images ({studentFaceImages.length})
              </h3>
              {studentFaceImages.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {studentFaceImages.map((image) => (
                    <div key={image.id} className="relative group">
                      <img 
                        src={image.image_path} 
                        alt="Face"
                        className="w-full h-32 object-cover rounded-lg border"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/placeholder-face.png';
                        }}
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                        <button
                          onClick={() => deleteFaceImage(image.id)}
                          className="bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="mt-1 text-xs text-center">
                        <span className={`inline-block px-2 py-1 rounded-full text-xs ${
                          image.has_embedding ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {image.has_embedding ? 'Processed' : 'Processing'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No face images uploaded yet. Upload some photos to enable face recognition.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
