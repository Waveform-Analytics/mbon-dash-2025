'use client';

import { motion } from 'framer-motion';
import { Waves, Clock, Users, Target } from 'lucide-react';

export default function ChallengePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">The Challenge</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex items-center justify-center min-h-[60vh]"
        >
          <div className="bg-card rounded-lg shadow-lg border p-12 text-center max-w-md">
            <Clock className="h-16 w-16 text-muted-foreground mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-card-foreground mb-4">Under Construction</h2>
            <p className="text-muted-foreground">
              This page is being rebuilt with the narrative-driven content about marine monitoring challenges and the ESONS foundation.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}