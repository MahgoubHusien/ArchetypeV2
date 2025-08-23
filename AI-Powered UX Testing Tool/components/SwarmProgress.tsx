import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { X, Eye, Bell } from 'lucide-react';
import { motion } from 'motion/react';

interface SwarmProgressProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  testConfig: any;
}

const OrganicBlob = ({ delay = 0, color = '#4F46E5' }) => {
  return (
    <motion.div
      className="absolute rounded-full blur-xl opacity-30"
      style={{
        background: `radial-gradient(circle, ${color}40 0%, transparent 70%)`,
        width: '120px',
        height: '120px',
      }}
      animate={{
        scale: [1, 1.2, 0.8, 1],
        x: [0, 30, -20, 0],
        y: [0, -15, 25, 0],
        rotate: [0, 180, 360],
      }}
      transition={{
        duration: 4,
        delay,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  );
};

const ParticleField = () => {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-[#4F46E5] rounded-full opacity-20"
          initial={{
            x: Math.random() * 400,
            y: Math.random() * 300,
          }}
          animate={{
            x: Math.random() * 400,
            y: Math.random() * 300,
            opacity: [0.2, 0.6, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
    </div>
  );
};

export function SwarmProgress({ isOpen, onClose, onComplete, testConfig }: SwarmProgressProps) {
  const [progress, setProgress] = useState(0);
  const [currentStatus, setCurrentStatus] = useState('Initializing agents...');
  const [agentCount] = useState(12);

  const statusMessages = [
    'Initializing agents...',
    'Loading target webpage...',
    'Analyzing DOM structure...',
    'Simulating user behaviors...',
    'Recording interactions...',
    'Processing results...',
    'Generating insights...'
  ];

  useEffect(() => {
    if (!isOpen) return;

    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + Math.random() * 8 + 2;
        
        // Update status message based on progress
        const statusIndex = Math.floor((newProgress / 100) * statusMessages.length);
        if (statusIndex < statusMessages.length) {
          setCurrentStatus(statusMessages[statusIndex]);
        }

        if (newProgress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            onComplete();
          }, 1000);
          return 100;
        }
        return newProgress;
      });
    }, 800);

    return () => clearInterval(interval);
  }, [isOpen, onComplete]);

  if (!isOpen) return null;

  const personaCount = testConfig?.personas?.length || 3;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-2xl p-8 w-full max-w-lg mx-4 shadow-2xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-[#1A1A1A]">Running UX Test</h2>
          <Button
            onClick={onClose}
            variant="ghost"
            size="icon"
            className="text-[#555] hover:text-[#1A1A1A]"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Organic Animation Container */}
        <div className="relative h-48 mb-6 bg-gradient-to-br from-[#F3F3F5] to-[#E9EBEF] rounded-xl overflow-hidden">
          <ParticleField />
          
          {/* Multiple organic blobs with different colors for personas */}
          <div className="absolute inset-0 flex items-center justify-center">
            <OrganicBlob delay={0} color="#EC4899" />
            <OrganicBlob delay={0.5} color="#3B82F6" />
            <OrganicBlob delay={1} color="#10B981" />
            <OrganicBlob delay={1.5} color="#8B5CF6" />
          </div>

          {/* Central glow */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          >
            <div className="w-32 h-32 bg-gradient-to-r from-[#4F46E5] to-[#7C3AED] rounded-full blur-2xl opacity-20" />
          </motion.div>
        </div>

        {/* Status Text */}
        <div className="text-center mb-6">
          <motion.h3
            key={currentStatus}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-[#1A1A1A] mb-2"
          >
            Simulating {agentCount} agents across {personaCount} personas...
          </motion.h3>
          <motion.p
            key={currentStatus + 'subtitle'}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[#555] mb-4"
          >
            {currentStatus}
          </motion.p>
          
          <Progress value={progress} className="mb-4" />
          <p className="text-sm text-[#555]">{Math.round(progress)}% complete</p>
        </div>

        {/* Background message */}
        <div className="bg-[#F3F3F5] rounded-xl p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-[#555] mb-2">
            <Bell className="w-4 h-4" />
            <span className="text-sm">Running in the background</span>
          </div>
          <p className="text-xs text-[#555]">
            You'll get a notification when results are ready
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-6">
          <Button
            onClick={onClose}
            variant="outline"
            className="flex-1 border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
          >
            Cancel Test
          </Button>
          <Button
            disabled={progress < 30}
            className="flex-1 bg-[#E9EBEF] text-[#555] hover:bg-[#CBCED4] border-none opacity-50"
          >
            <Eye className="w-4 h-4 mr-2" />
            View Partial Results
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
}