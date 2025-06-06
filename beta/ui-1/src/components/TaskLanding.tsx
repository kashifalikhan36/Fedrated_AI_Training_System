import { useState, useEffect } from 'react';
import { Clock, Shield, DollarSign, ArrowRight } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const TaskLanding = () => {
  const [estimatedTime, setEstimatedTime] = useState<number>(0);
  const [taskInfo, setTaskInfo] = useState<{ time: string, earn: string }>({ time: '—', earn: '—' });

  useEffect(() => {
    const calculateEstimatedTime = () => {
      const startTime = performance.now();
      let result = 0;
      for (let i = 0; i < 1000000; i++) {
        result += Math.random();
      }
      const endTime = performance.now();
      const devicePerformance = endTime - startTime;
      const baseTime = 300;
      const estimatedSeconds = Math.round(baseTime * (devicePerformance / 100));
      setEstimatedTime(Math.max(180, Math.min(600, estimatedSeconds)));
    };

    calculateEstimatedTime();
  }, []);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleStartTask = async () => {
    try {
      const res = await fetch("http://20.244.34.219:5000/get_model_train_data");
      const data = await res.json();
      setTaskInfo(data);
    } catch (err) {
      console.error("Error fetching start task data:", err);
    }
  };

  const handleSkipTask = async () => {
    try {
      const res = await fetch("http://20.244.34.219:5000/new_model_info_train");
      const data = await res.json();
      setTaskInfo(data);
    } catch (err) {
      console.error("Error fetching skip task data:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-6 sm:text-5xl">
            Distributed Ai Training Tasks
          </h1>
          <p className="text-xl text-gray-600">
            Your next task is ready. Complete it securely and earn rewards.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-12">
          {/* Time Estimation Card */}
          <Card className="p-6 backdrop-blur-sm bg-white/90 border border-purple-100 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex flex-col items-center">
              <Clock className="w-12 h-12 text-purple-600 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Estimated Time</h2>
              <p className="text-3xl font-bold text-purple-600 mb-2">
                {taskInfo.time !== '—' ? taskInfo.time : formatTime(estimatedTime)}
              </p>
              <p className="text-sm text-gray-500 text-center">
                Based on your device performance
              </p>
            </div>
          </Card>

          {/* Security Card */}
          <Card className="p-6 backdrop-blur-sm bg-white/90 border border-purple-100 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex flex-col items-center">
              <Shield className="w-12 h-12 text-purple-600 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Secure & Transparent</h2>
              <p className="text-sm text-gray-500 text-center">
                Task runs with encrypted hyperparameters for your security and privacy
              </p>
            </div>
          </Card>

          {/* Earnings Card */}
          <Card className="p-6 backdrop-blur-sm bg-white/90 border border-purple-100 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex flex-col items-center">
              <DollarSign className="w-12 h-12 text-purple-600 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Your Earnings</h2>
              <p className="text-3xl font-bold text-purple-600 mb-2">
                ${taskInfo.earn !== '—' ? taskInfo.earn : '00.00'}
              </p>
              <p className="text-sm text-gray-500 text-center">
                Paid instantly upon completion
              </p>
            </div>
          </Card>
        </div>

        {/* CTA Buttons */}
        <div className="flex justify-center space-x-4">
          <Button
            onClick={handleStartTask}
            className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-6 text-lg rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
          >
            Start Task
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            onClick={handleSkipTask}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-8 py-6 text-lg rounded-lg shadow-md transition-all transform hover:scale-105"
          >
            Skip Task
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TaskLanding;
