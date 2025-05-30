/**
 * Mouse Tracker Library
 * 
 * This library provides functionality to track mouse events and send them to a tracking server.
 * It supports tracking mouse movements, clicks, scrolls, and form interactions.
 */

import { v4 as uuidv4 } from 'uuid';

export interface TrackerOptions {
  apiEndpoint?: string;
  wsEndpoint?: string;
  trackMouseMove?: boolean;
  trackMouseClick?: boolean;
  trackScroll?: boolean;
  trackForms?: boolean;
  sampleRate?: number;
  batchSize?: number;
  batchInterval?: number;
}

export interface TrackingEvent {
  event_type: string;
  timestamp: string;
  url: string;
  session_id: string;
  data: any;
}

class MouseTracker {
  private options: TrackerOptions;
  private sessionId: string;
  private userAgent: string;
  private queue: TrackingEvent[];
  private isConnected: boolean;
  private ws: WebSocket | null;
  private eventCount: number;
  private lastMousePosition: { x: number, y: number } | null;
  private throttleTimeout: NodeJS.Timeout | null;
  private batchTimeout: NodeJS.Timeout | null;
  
  constructor(options: TrackerOptions = {}) {
    this.options = {
      apiEndpoint: process.env.NEXT_PUBLIC_TRACKER_API_ENDPOINT || 'http://localhost:8000/api/v1/tracking/events',
      wsEndpoint: process.env.NEXT_PUBLIC_TRACKER_WS_ENDPOINT || 'ws://localhost:8000/ws/tracking',
      trackMouseMove: true,
      trackMouseClick: true,
      trackScroll: true,
      trackForms: true,
      sampleRate: 0.1, // Sample 10% of mouse move events
      batchSize: 10,
      batchInterval: 1000, // Send batch every 1 second
      ...options
    };
    
    this.sessionId = this.getSessionId();
    this.userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : '';
    this.queue = [];
    this.isConnected = false;
    this.ws = null;
    this.eventCount = 0;
    this.lastMousePosition = null;
    this.throttleTimeout = null;
    this.batchTimeout = null;
  }
  
  /**
   * Initialize the tracker and attach event listeners
   */
  init(): void {
    if (typeof window === 'undefined') return; // Skip if not in browser
    
    // Create or get session
    this.createSession();
    
    // Connect WebSocket if available
    this.connectWebSocket();
    
    // Attach event listeners
    this.attachEventListeners();
    
    // Start batch processing
    this.startBatchProcessing();
    
    console.log('Mouse tracker initialized with session ID:', this.sessionId);
  }
  
  /**
   * Get or create a session ID
   */
  private getSessionId(): string {
    if (typeof localStorage !== 'undefined') {
      const storedId = localStorage.getItem('mouse_tracker_session_id');
      if (storedId) return storedId;
      
      const newId = uuidv4();
      localStorage.setItem('mouse_tracker_session_id', newId);
      return newId;
    }
    
    return uuidv4();
  }
  
  /**
   * Create a session on the server
   */
  private createSession(): void {
    const sessionData = {
      session_id: this.sessionId,
      user_agent: this.userAgent,
      referrer: document.referrer,
      is_active: true
    };
    
    fetch(`${this.options.apiEndpoint?.replace('/events', '/sessions')}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(sessionData)
    }).catch(error => {
      console.error('Error creating tracking session:', error);
    });
  }
  
  /**
   * Connect to WebSocket server for real-time tracking
   */
  private connectWebSocket(): void {
    if (!this.options.wsEndpoint || typeof WebSocket === 'undefined') return;
    
    try {
      this.ws = new WebSocket(this.options.wsEndpoint);
      
      this.ws.onopen = () => {
        this.isConnected = true;
        console.log('WebSocket connection established');
      };
      
      this.ws.onclose = () => {
        this.isConnected = false;
        console.log('WebSocket connection closed');
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectWebSocket(), 5000);
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }
  
  /**
   * Attach event listeners based on configuration
   */
  private attachEventListeners(): void {
    if (typeof window === 'undefined') return;
    
    // Track mouse moves
    if (this.options.trackMouseMove) {
      window.addEventListener('mousemove', this.handleMouseMove.bind(this));
    }
    
    // Track mouse clicks
    if (this.options.trackMouseClick) {
      window.addEventListener('click', this.handleMouseClick.bind(this));
    }
    
    // Track scrolling
    if (this.options.trackScroll) {
      window.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
    }
    
    // Track form interactions
    if (this.options.trackForms) {
      document.addEventListener('input', this.handleFormInput.bind(this));
      document.addEventListener('change', this.handleFormChange.bind(this));
      document.addEventListener('submit', this.handleFormSubmit.bind(this));
    }
    
    // Track page visibility
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    
    // Track page unload
    window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
    
    // Track page view on initialization
    this.trackEvent('page_view', {
      title: document.title,
      path: window.location.pathname
    });
  }
  
  /**
   * Handle mouse move events with throttling and sampling
   */
  private handleMouseMove(event: MouseEvent): void {
    // Sample only a percentage of mousemove events to reduce volume
    if (Math.random() > (this.options.sampleRate || 0.1)) return;
    
    // Throttle mouse move events
    if (this.throttleTimeout) return;
    
    this.throttleTimeout = setTimeout(() => {
      this.throttleTimeout = null;
      
      const { clientX, clientY } = event;
      
      // Skip if position hasn't changed significantly
      if (this.lastMousePosition && 
          Math.abs(this.lastMousePosition.x - clientX) < 10 &&
          Math.abs(this.lastMousePosition.y - clientY) < 10) {
        return;
      }
      
      this.lastMousePosition = { x: clientX, y: clientY };
      
      this.trackEvent('mouse_move', {
        x: clientX,
        y: clientY,
        window_width: window.innerWidth,
        window_height: window.innerHeight
      });
    }, 100); // Throttle to max 10 events per second
  }
  
  /**
   * Handle mouse click events
   */
  private handleMouseClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    
    this.trackEvent('mouse_click', {
      x: event.clientX,
      y: event.clientY,
      button: event.button,
      element_tag: target.tagName.toLowerCase(),
      element_id: target.id || null,
      element_class: target.className || null,
      window_width: window.innerWidth,
      window_height: window.innerHeight
    });
  }
  
  /**
   * Handle scroll events with throttling
   */
  private handleScroll(event: Event): void {
    if (this.throttleTimeout) return;
    
    this.throttleTimeout = setTimeout(() => {
      this.throttleTimeout = null;
      
      this.trackEvent('scroll', {
        scroll_x: window.scrollX,
        scroll_y: window.scrollY,
        document_height: document.documentElement.scrollHeight,
        viewport_height: window.innerHeight
      });
    }, 200);
  }
  
  /**
   * Handle form input events
   */
  private handleFormInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    const inputType = target.type || 'text';
    
    // Don't track password inputs
    if (inputType === 'password') return;
    
    this.trackEvent('form_input', {
      element_tag: target.tagName.toLowerCase(),
      element_id: target.id || null,
      element_name: target.name || null,
      input_type: inputType,
      has_value: !!target.value
    });
  }
  
  /**
   * Handle form change events (select, checkbox, etc)
   */
  private handleFormChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    
    this.trackEvent('form_change', {
      element_tag: target.tagName.toLowerCase(),
      element_id: target.id || null,
      element_name: target.name || null,
      input_type: target.type || 'text',
      has_value: !!target.value
    });
  }
  
  /**
   * Handle form submission events
   */
  private handleFormSubmit(event: Event): void {
    const target = event.target as HTMLFormElement;
    
    this.trackEvent('form_submit', {
      form_id: target.id || null,
      form_action: target.action || null,
      form_method: target.method || 'get'
    });
  }
  
  /**
   * Handle page visibility changes
   */
  private handleVisibilityChange(): void {
    this.trackEvent('visibility_change', {
      is_visible: !document.hidden
    });
  }
  
  /**
   * Handle page unload event
   */
  private handleBeforeUnload(): void {
    // Flush queue immediately before page unloads
    this.flushQueue(true);
    
    this.trackEvent('page_unload', {
      title: document.title,
      path: window.location.pathname
    }, true);
  }
  
  /**
   * Track a custom event
   */
  trackCustomEvent(eventName: string, data: any): void {
    this.trackEvent(`custom_${eventName}`, data);
  }
  
  /**
   * Internal method to track any event
   */
  private trackEvent(eventType: string, data: any, immediate = false): void {
    const event: TrackingEvent = {
      event_type: eventType,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      session_id: this.sessionId,
      data: data
    };
    
    // Send via WebSocket if connected
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(event));
      } catch (error) {
        console.error('Error sending event via WebSocket:', error);
      }
    }
    
    // Add to queue for HTTP sending
    this.queue.push(event);
    this.eventCount++;
    
    // Send immediately if requested or queue is full
    if (immediate || this.queue.length >= (this.options.batchSize || 10)) {
      this.flushQueue(immediate);
    }
  }
  
  /**
   * Start batch processing timer
   */
  private startBatchProcessing(): void {
    if (this.batchTimeout) clearInterval(this.batchTimeout);
    
    this.batchTimeout = setInterval(() => {
      if (this.queue.length > 0) {
        this.flushQueue();
      }
    }, this.options.batchInterval || 1000);
  }
  
  /**
   * Flush the event queue to the server
   */
  private flushQueue(immediate = false): void {
    if (this.queue.length === 0) return;
    
    const events = [...this.queue];
    this.queue = [];
    
    const sendEvents = () => {
      fetch(this.options.apiEndpoint || '', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(events),
        // Use keepalive for unload events
        keepalive: immediate
      }).catch(error => {
        console.error('Error sending tracking events:', error);
        
        // Put events back in queue on failure, if not during page unload
        if (!immediate) {
          this.queue = [...events, ...this.queue];
        }
      });
    };
    
    // Use sendBeacon if available and this is an immediate flush (page unload)
    if (immediate && navigator.sendBeacon) {
      try {
        const blob = new Blob([JSON.stringify(events)], { type: 'application/json' });
        navigator.sendBeacon(this.options.apiEndpoint || '', blob);
      } catch (error) {
        console.error('Error using sendBeacon:', error);
        sendEvents();
      }
    } else {
      sendEvents();
    }
  }
  
  /**
   * Manually end the tracking session
   */
  endSession(): void {
    // Flush any remaining events
    this.flushQueue(true);
    
    // Close the WebSocket connection
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    // Notify the server that the session has ended
    fetch(`${this.options.apiEndpoint?.replace('/events', '/sessions')}/${this.sessionId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    }).catch(error => {
      console.error('Error ending tracking session:', error);
    });
    
    console.log('Mouse tracking session ended');
  }
}

export default MouseTracker; 