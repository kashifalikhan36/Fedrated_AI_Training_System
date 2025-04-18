import React from 'react';
import { CheckCircle } from 'lucide-react';

const CompletionMessage: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full text-center">
      <div className="flex justify-center mb-4">
        <CheckCircle className="w-16 h-16 text-green-600" />
      </div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">All Tasks Completed!</h2>
      <p className="text-gray-600 mb-6">
        You've completed all available tasks. The application will close shortly.
      </p>
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
        <div 
          className="bg-green-600 h-2.5 rounded-full animate-pulse"
          style={{ width: '100%' }}
        ></div>
      </div>
      <p className="text-sm text-gray-500">The app will close automatically...</p>
    </div>
  );
};

export default CompletionMessage;