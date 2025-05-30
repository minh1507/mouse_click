'use client';

import { useEffect } from 'react';
import MouseTracker from '@/lib/tracker';

/**
 * Component that initializes the mouse tracker on the client side
 * Should be included in pages where tracking is needed
 */
export default function TrackerInitializer() {
  useEffect(() => {
    // Initialize tracker only on client side
    const tracker = new MouseTracker({
      // Custom options can be passed here if needed
      trackMouseMove: true,
      trackMouseClick: true,
      trackScroll: true,
      trackForms: true,
      sampleRate: 0.1, // Only track 10% of mouse move events to reduce volume
    });
    
    // Initialize tracker
    tracker.init();
    
    // Clean up tracker when component unmounts
    return () => {
      // End the tracking session when the component unmounts
      tracker.endSession();
    };
  }, []);
  
  // This component doesn't render anything visible
  return null;
} 