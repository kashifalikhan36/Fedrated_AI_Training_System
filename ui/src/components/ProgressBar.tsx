import React from 'react';

interface ProgressBarProps {
  totalTasks: number;
  completedTasks: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ totalTasks, completedTasks }) => {
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  
  return (
    <div className="mb-6">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">
          Progress: {completedTasks} of {totalTasks} tasks completed
        </span>
        <span className="text-sm font-medium text-blue-600">
          {Math.round(progress)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar;