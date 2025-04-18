import React from 'react';
import { ClipboardList } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm mb-8">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center">
        <ClipboardList className="h-8 w-8 text-blue-600 mr-3" />
        <h1 className="text-2xl font-bold text-gray-800">Task Management Portal</h1>
      </div>
    </header>
  );
};

export default Header;