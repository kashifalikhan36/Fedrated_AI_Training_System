export interface Task {
  id: number;
  title: string;
  description: string;
  category: string;
  time: string;
  payout: string;
}

export interface TaskState {
  tasks: Task[];
  currentTaskIndex: number;
  completedTasks: number[];
  isLoading: boolean;
  error: string | null;
}