import React, { useState, useEffect } from 'react';
import TaskCard from './components/TaskCard';
import ProgressBar from './components/ProgressBar';
import CompletionMessage from './components/CompletionMessage';
import Header from './components/Header';
import { dummyTasks } from './data/tasks';
import { startFinetune } from './services/api';
import { Task } from './types';

function App() {
  const [tasks] = useState<Task[]>(dummyTasks);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [completedTasks, setCompletedTasks] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [allTasksCompleted, setAllTasksCompleted] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('Processing...');
  
  // Check if we have completed all tasks
  useEffect(() => {
    if (completedTasks.length === tasks.length) {
      setAllTasksCompleted(true);
      
      // In a real app, this would close the application after a short delay
      // For demo purposes, we're just showing the completion message
      const timer = setTimeout(() => {
        console.log('Application would close here in a real environment');
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [completedTasks, tasks.length]);
  
  // Handle accepting a task
  const handleAcceptTask = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setProcessingMessage('Processing task, please wait...');
    
    try {
      // Call the API to start finetune
      const result = await startFinetune();
      
      if (result.success) {
        setProcessingMessage(result.message); // Will show "OK"
        await new Promise(resolve => setTimeout(resolve, 1000)); // Show "OK" for 1 second
        
        // Mark current task as completed
        setCompletedTasks(prev => [...prev, tasks[currentTaskIndex].id]);
        
        // Move to next available task if any
        findNextAvailableTask();
      } else {
        console.error('Failed to accept task:', result.message);
        setProcessingMessage('Failed to process task');
      }
    } catch (error) {
      console.error('Error accepting task:', error);
      setProcessingMessage('Error processing task');
    } finally {
      setIsLoading(false);
      setProcessingMessage('Processing...');
    }
  };
  
  // Handle skipping a task
  const handleSkipTask = () => {
    if (isLoading) return;
    findNextAvailableTask();
  };
  
  // Find the next available task
  const findNextAvailableTask = () => {
    const remainingTasks = tasks.filter(task => !completedTasks.includes(task.id));
    
    if (remainingTasks.length > 0) {
      // Find the index of the next uncompleted task
      const nextTaskIndex = tasks.findIndex(
        (task, index) => index > currentTaskIndex && !completedTasks.includes(task.id)
      );
      
      if (nextTaskIndex !== -1) {
        // We found a task after the current one
        setCurrentTaskIndex(nextTaskIndex);
      } else {
        // Wrap around to the beginning of the list
        const firstAvailableIndex = tasks.findIndex(task => !completedTasks.includes(task.id));
        setCurrentTaskIndex(firstAvailableIndex);
      }
    } else {
      // No tasks remaining, all completed
      setAllTasksCompleted(true);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <main className="max-w-5xl mx-auto px-4 pb-12">
        {!allTasksCompleted ? (
          <>
            <ProgressBar 
              totalTasks={tasks.length} 
              completedTasks={completedTasks.length} 
            />
            
            <div className="flex justify-center">
              {tasks[currentTaskIndex] && (
                <TaskCard
                  task={tasks[currentTaskIndex]}
                  onAccept={handleAcceptTask}
                  onSkip={handleSkipTask}
                  isLoading={isLoading}
                  processingMessage={processingMessage}
                />
              )}
            </div>
          </>
        ) : (
          <div className="flex justify-center">
            <CompletionMessage />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;