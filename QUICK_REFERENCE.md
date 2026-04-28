# React Pages Quick Reference Guide

## 📋 Page Overview

### Authentication Pages

```
/login          → Login with username/password
/signup         → Register new account with role selection
```

### Main Dashboard

```
/                → Statistics & overview (4 cards)
```

### Management Pages (Full CRUD)

```
/students       → Student management with add/edit/delete
/classes        → Class management with add/edit/delete
/sessions       → Session management with add/edit/delete
```

### Operational Pages

```
/live-camera    → Real-time face recognition capture
/attendance     → View attendance history with export
/reports        → Generate reports with export options
/settings       → System configuration & logout
```

## 🔧 Development Tips

### Adding a New CRUD Page

1. **Create the page file** (`pages/NewEntity.tsx`):

```tsx
import React, { useState, useEffect } from "react";
import { Plus, Edit2, Trash2 } from "lucide-react";
import api from "../services/api";

export default function NewEntity() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ field1: "", field2: "" });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const { data } = await api.get("/endpoint/");
      setItems(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // ... rest of CRUD logic
}
```

2. **Add route in App.tsx**:

```tsx
<Route
  path="/new-entity"
  element={
    <ProtectedRoute>
      <NewEntity />
    </ProtectedRoute>
  }
/>
```

3. **Add to Sidebar** (`components/Sidebar.tsx`):

```tsx
const navigation = [
  // ... existing items
  { name: "New Entity", href: "/new-entity", icon: IconComponent },
];
```

### API Call Patterns

**GET (List)**:

```tsx
const { data } = await api.get("/endpoint/");
```

**POST (Create)**:

```tsx
await api.post("/endpoint/", formData);
```

**PUT (Update)**:

```tsx
await api.put(`/endpoint/${id}`, formData);
```

**DELETE**:

```tsx
await api.delete(`/endpoint/${id}`);
```

**Export/Download**:

```tsx
const { data } = await api.get("/endpoint/export", { responseType: "blob" });
const url = window.URL.createObjectURL(new Blob([data]));
// ... create download link
```

### Form Modal Pattern

```tsx
const openModal = (item: any = null) => {
  if (item) {
    setEditingId(item.id);
    setFormData({ ...item });
  } else {
    setEditingId(null);
    setFormData({ field1: "", field2: "" });
  }
  setShowModal(true);
};

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    if (editingId) {
      await api.put(`/endpoint/${editingId}`, formData);
    } else {
      await api.post("/endpoint/", formData);
    }
    setShowModal(false);
    fetchItems();
  } catch (e) {
    console.error(e);
  }
};
```

## 🎨 Styling Guidelines

**Tailwind Classes Used**:

- Colors: `indigo-600`, `green-600`, `red-600`, `gray-*`
- Layout: `space-y-6`, `flex`, `grid`, `gap-4`
- Tables: `min-w-full`, `divide-y`, `divide-gray-200`
- Buttons: `px-4 py-2 rounded-lg flex items-center gap-2`
- Modals: `fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50`

## 🔐 Authentication

**Check if logged in**:

```tsx
const { token, user, login, logout } = useAuth();
```

**Protected page example**:

```tsx
<Route
  path="/page"
  element={
    <ProtectedRoute>
      <Page />
    </ProtectedRoute>
  }
/>
```

**Logout**:

```tsx
const { logout } = useAuth();
onClick = { logout };
```

## 📊 Common State Patterns

**Loading + Data**:

```tsx
const [data, setData] = useState<any[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetch = async () => {
    try {
      const { data } = await api.get("/endpoint/");
      setData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };
  fetch();
}, []);

if (loading) return <div>Loading...</div>;
```

**Modal Control**:

```tsx
const [showModal, setShowModal] = useState(false);
const [editingId, setEditingId] = useState<string | null>(null);

const openModal = (item: any = null) => {
  if (item) setEditingId(item.id);
  else setEditingId(null);
  setShowModal(true);
};
```

**Form Data**:

```tsx
const [formData, setFormData] = useState({ field1: '', field2: '' });

// In input
onChange={(e) => setFormData({ ...formData, field1: e.target.value })}
```

## 🧪 Testing API Integration

1. **Use browser DevTools**:
   - Network tab to see requests
   - Check headers for Authorization token
   - Verify response data

2. **Check localStorage**:

   ```javascript
   localStorage.getItem("token");
   ```

3. **Test API manually**:
   ```bash
   curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/endpoint
   ```

## ⚠️ Common Issues

**Token not sent**:

- Check localStorage for token: `localStorage.getItem('token')`
- Verify interceptor in `api.ts` is configured
- Check API response headers

**CORS errors**:

- Backend must have CORS enabled for frontend URL
- Check `Access-Control-Allow-Origin` header

**Modals not closing**:

- Ensure `setShowModal(false)` is called after operation
- Check form submission isn't prevented

**Loading stays true**:

- Check `finally` block has `setLoading(false)`
- Verify API response handling

## 📱 Responsive Design

All pages are responsive using:

- `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` - Responsive grids
- `max-w-md` / `max-w-lg` - Max widths
- Flexbox for horizontal layouts
- Tailwind breakpoints (sm, md, lg, xl)

## 🚀 Performance Tips

1. **Memoize expensive components**:

   ```tsx
   const MemoizedTable = React.memo(TableComponent);
   ```

2. **Debounce search**:

   ```tsx
   import { debounce } from "lodash";
   const debouncedSearch = debounce(searchFunction, 300);
   ```

3. **Lazy load pages**:
   ```tsx
   const Students = lazy(() => import("./pages/Students"));
   ```

## 📚 File Locations

| What          | Where                                   |
| ------------- | --------------------------------------- |
| Pages         | `frontend/src/pages/*.tsx`              |
| API Service   | `frontend/src/services/api.ts`          |
| Auth Context  | `frontend/src/contexts/AuthContext.tsx` |
| Navbar        | `frontend/src/components/Navbar.tsx`    |
| Sidebar       | `frontend/src/components/Sidebar.tsx`   |
| Router Config | `frontend/src/App.tsx`                  |
| Environment   | `.env` or `vite.config.ts`              |

## 🔗 API Integration Checklist

- [ ] API base URL configured in `api.ts`
- [ ] Auth endpoints implemented (/login, /signup, /auth/me)
- [ ] CRUD endpoints for each entity
- [ ] Export endpoints configured
- [ ] Error handling matches frontend expectations
- [ ] CORS enabled for frontend origin
- [ ] Bearer token validation in backend
- [ ] Response format matches frontend expectations

All pages ready for production use!
