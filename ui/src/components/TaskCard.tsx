import React from 'react';
import { Clock, DollarSign, CheckCircle, SkipForward } from 'lucide-react';
import { Task } from '../types';

interface TaskCardProps {
  task: Task;
  onAccept: () => void;
  onSkip: () => void;
  isLoading: boolean;
  processingMessage: string;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onAccept, onSkip, isLoading, processingMessage }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-md w-full transition-all duration-300 hover:shadow-lg">
      <div className="mb-2 inline-block px-2 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-md">
        {task.category}
      </div>
      
      <h2 className="text-xl font-bold text-gray-800 mb-2">{task.title}</h2>
      <p className="text-gray-600 mb-4">{task.description}</p>
      
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center text-gray-700">
          <Clock className="w-5 h-5 mr-2 text-blue-600" />
          <span className="font-medium">Time: {task.time}</span>
        </div>
        
        <div className="flex items-center text-gray-700">
          <DollarSign className="w-5 h-5 mr-2 text-green-600" />
          <span className="font-medium">Payout: {task.payout}</span>
        </div>
      </div>
      
      {isLoading && (
        <div className="mb-4 text-center text-blue-600">
          <div className="animate-pulse">{processingMessage}</div>
        </div>
      )}
      
      <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
        <button
          onClick={onAccept}
          disabled={isLoading}
          className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-white font-medium transition-colors duration-300 ${
            isLoading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50'
          }`}
        >
          <CheckCircle className="w-5 h-5 mr-2" />
          {isLoading ? 'Processing...' : 'Accept Task'}
        </button>
        
        <button
          onClick={onSkip}
          disabled={isLoading}
          className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md font-medium transition-colors duration-300 ${
            isLoading
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50'
          }`}
        >
          <SkipForward className="w-5 h-5 mr-2" />
          Skip Task
        </button>
      </div>
    </div>
  );
};

export default TaskCard;