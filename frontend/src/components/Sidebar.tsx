import { NavLink } from 'react-router-dom';
import { LayoutDashboard as LayoutIcon, Users as UsersIcon, UserCheck as UserCheckIcon, Settings as SettingsIcon, BookOpen, Clock, Camera, FileText } from 'lucide-react';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutIcon },
  { name: 'Students', href: '/students', icon: UsersIcon },
  { name: 'Classes', href: '/classes', icon: BookOpen },
  { name: 'Sessions', href: '/sessions', icon: Clock },
  { name: 'Live Camera', href: '/live-camera', icon: Camera },
  { name: 'Attendance', href: '/attendance', icon: UserCheckIcon },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
];

export default function Sidebar() {
  return (
    <div className="flex flex-col w-64 bg-white border-r">
      <div className="flex items-center justify-center h-16 border-b px-4">
        <h1 className="text-xl font-bold text-gray-900 truncate">Smart Face System</h1>
      </div>
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
