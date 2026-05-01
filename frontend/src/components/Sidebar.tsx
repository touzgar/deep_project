import { NavLink } from 'react-router-dom';
import { LayoutDashboard as LayoutIcon, Users as UsersIcon, UserCheck as UserCheckIcon, Settings as SettingsIcon, BookOpen, Clock, Camera, FileText } from 'lucide-react';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { useAuth } from '../contexts/AuthContext';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Define navigation items with role-based access
const allNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutIcon, roles: ['admin', 'teacher'] },
  { name: 'Students', href: '/students', icon: UsersIcon, roles: ['admin', 'teacher'] },
  { name: 'Classes', href: '/classes', icon: BookOpen, roles: ['admin', 'teacher'] },
  { name: 'Sessions', href: '/sessions', icon: Clock, roles: ['admin', 'teacher'] },
  { name: 'Live Camera', href: '/live-camera', icon: Camera, roles: ['admin', 'teacher'] },
  { name: 'Attendance', href: '/attendance', icon: UserCheckIcon, roles: ['admin', 'teacher'] },
  { name: 'Reports', href: '/reports', icon: FileText, roles: ['admin', 'teacher'] },
  { name: 'Profile', href: '/settings', icon: SettingsIcon, roles: ['admin', 'teacher'] }, // Both can access
];

export default function Sidebar() {
  const { user } = useAuth();

  // Filter navigation based on user role
  const navigation = allNavigation.filter(item => 
    user && item.roles.includes(user.role)
  );

  return (
    <div className="flex flex-col w-64 bg-white border-r">
      <div className="flex items-center justify-center h-16 border-b px-4">
        <h1 className="text-xl font-bold text-gray-900 truncate">Smart Face System</h1>
      </div>
      
      {/* User Role Badge */}
      {user && (
        <div className="px-5 py-3 border-b bg-gray-50">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">
                {user.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user.username}</p>
              <p className="text-xs text-gray-500 capitalize">{user.role}</p>
            </div>
          </div>
        </div>
      )}

      <div className="overflow-y-auto overflow-x-hidden flex-grow">
        <ul className="flex flex-col py-4 space-y-1">
          {navigation.map((item) => (
            <li key={item.name} className="px-5">
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "relative flex flex-row items-center h-11 focus:outline-none hover:bg-gray-50 text-gray-600 hover:text-gray-800 border-l-4 border-transparent pr-6",
                    isActive ? "border-indigo-500 text-indigo-600 bg-indigo-50 hover:bg-indigo-50 hover:text-indigo-700" : ""
                  )
                }
              >
                <span className="inline-flex justify-center items-center ml-4">
                  <item.icon className="w-5 h-5" />
                </span>
                <span className="ml-2 text-sm tracking-wide truncate">{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
