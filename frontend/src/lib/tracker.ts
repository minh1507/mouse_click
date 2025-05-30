/**
 * MouseTracker - JavaScript library for tracking mouse behavior
 * 
 * This library collects mouse events (movements, clicks, scrolls) and 
 * sends them to the backend for analysis.
 */

interface TrackerOptions {
  apiUrl?: string;
  trackMouseMove?: boolean;
  trackMouseClick?: boolean;
  trackScroll?: boolean;
  trackForms?: boolean;
  sampleRate?: number;
  sessionTimeout?: number;
  websocketUrl?: string;
  batchSize?: number;
  batchInterval?: number;
}

interface TrackingEvent {
  event_type: string;
  timestamp: number;
  url: string;
  session_id: string;
  data: Record<string, any>;
}

class MouseTracker {
  private options: TrackerOptions;
  private sessionId: string;
  private isActive: boolean;
  private events: TrackingEvent[];
  private lastActivity: number;
  private batchTimeout: NodeJS.Timeout | null;
  private websocket: WebSocket | null;
  private moveCounter: number;
  
  constructor(options: TrackerOptions = {}) {
    // Default options
    this.options = {
      apiUrl: '/api/tracking/events',
      trackMouseMove: true,
      trackMouseClick: true,
      trackScroll: true,
      trackForms: true,
      sampleRate: 0.2, // Only track 20% of mouse move events by default
      sessionTimeout: 30 * 60 * 1000, // 30 minutes
      websocketUrl: undefined,
      batchSize: 10,
      batchInterval: 5000, // 5 seconds
      ...options
    };
    
    // Initialize state
    this.sessionId = this.generateSessionId();
    this.isActive = false;
    this.events = [];
    this.lastActivity = Date.now();
    this.batchTimeout = null;
    this.websocket = null;
    this.moveCounter = 0;
  }
  
  /**
   * Initialize the tracker and start collecting events
   */
  public init(): void {
    if (this.isActive) return;
    
    // Register event listeners
    if (this.options.trackMouseMove) {
      document.addEventListener('mousemove', this.handleMouseMove);
    }
    
    if (this.options.trackMouseClick) {
      document.addEventListener('click', this.handleMouseClick);
    }
    
    if (this.options.trackScroll) {
      window.addEventListener('scroll', this.handleScroll);
    }
    
    if (this.options.trackForms) {
      document.addEventListener('input', this.handleFormInput);
      document.addEventListener('change', this.handleFormChange);
    }
    
    // Track page views
    this.trackEvent('page_view', {
      title: document.title,
      referrer: document.referrer
    });
    
    // Initialize WebSocket if needed
    if (this.options.websocketUrl) {
      this.initWebSocket();
    }
    
    // Start batch timer
    this.startBatchTimer();
    
    // Start session activity monitoring
    window.addEventListener('beforeunload', this.handleBeforeUnload);
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
    
    this.isActive = true;
    
    // Create a session on the server
    this.createSession();
  }
  
  /**
   * End the tracking session
   */
  public endSession(): void {
    if (!this.isActive) return;
    
    // Remove event listeners
    if (this.options.trackMouseMove) {
      document.removeEventListener('mousemove', this.handleMouseMove);
    }
    
    if (this.options.trackMouseClick) {
      document.removeEventListener('click', this.handleMouseClick);
    }
    
    if (this.options.trackScroll) {
      window.removeEventListener('scroll', this.handleScroll);
    }
    
    if (this.options.trackForms) {
      document.removeEventListener('input', this.handleFormInput);
      document.removeEventListener('change', this.handleFormChange);
    }
    
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    
    // Close WebSocket
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    // Clear batch timer
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }
    
    // Send any remaining events
    this.sendEvents();
    
    this.isActive = false;
    
    // Update session end time on the server
    this.updateSession();
  }
  
  /**
   * Track a custom event
   */
  public trackEvent(eventType: string, data: Record<string, any> = {}): void {
    if (!this.isActive) return;
    
    const event: TrackingEvent = {
      event_type: eventType,
      timestamp: Date.now(),
      url: window.location.href,
      session_id: this.sessionId,
      data
    };
    
    this.events.push(event);
    this.lastActivity = Date.now();
    
    // Send immediately via WebSocket if available
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(event));
    } 
    // Otherwise, send batch if it's full
    else if (this.events.length >= this.options.batchSize!) {
      this.sendEvents();
    }
  }
  
  /**
   * Handle mouse move events
   */
  private handleMouseMove = (e: MouseEvent): void => {
    // Sample mouse move events to reduce volume
    this.moveCounter++;
    if (this.moveCounter % Math.floor(1 / this.options.sampleRate!) !== 0) {
      return;
    }
    
    this.trackEvent('mouse_move', {
      x: e.clientX,
      y: e.clientY,
      screenX: e.screenX,
      screenY: e.screenY,
      target: this.getElementInfo(e.target as HTMLElement)
    });
  };
  
  /**
   * Handle mouse click events
   */
  private handleMouseClick = (e: MouseEvent): void => {
    this.trackEvent('mouse_click', {
      x: e.clientX,
      y: e.clientY,
      button: e.button,
      target: this.getElementInfo(e.target as HTMLElement)
    });
  };
  
  /**
   * Handle scroll events
   */
  private handleScroll = (): void => {
    this.trackEvent('scroll', {
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      scrollHeight: document.documentElement.scrollHeight,
      scrollWidth: document.documentElement.scrollWidth,
      viewportHeight: window.innerHeight,
      viewportWidth: window.innerWidth
    });
  };
  
  /**
   * Handle form input events
   */
  private handleFormInput = (e: Event): void => {
    const target = e.target as HTMLInputElement;
    
    this.trackEvent('form_input', {
      field: this.getElementInfo(target),
      fieldType: target.type,
      formId: this.getFormId(target)
    });
  };
  
  /**
   * Handle form change events
   */
  private handleFormChange = (e: Event): void => {
    const target = e.target as HTMLInputElement;
    
    this.trackEvent('form_change', {
      field: this.getElementInfo(target),
      fieldType: target.type,
      formId: this.getFormId(target),
      value: target.type === 'password' ? '***' : target.value
    });
  };
  
  /**
   * Handle beforeunload event
   */
  private handleBeforeUnload = (): void => {
    // Send remaining events synchronously
    if (this.events.length > 0) {
      // Use synchronous XHR to ensure data is sent before page unload
      const xhr = new XMLHttpRequest();
      xhr.open('POST', this.options.apiUrl!, false); // Synchronous request
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(this.events));
      this.events = [];
    }
    
    this.updateSession();
  };
  
  /**
   * Handle visibility change event
   */
  private handleVisibilityChange = (): void => {
    if (document.visibilityState === 'hidden') {
      // User switched tabs or minimized browser
      this.sendEvents();
    } else {
      // User returned to the page
      this.trackEvent('page_focus', {
        title: document.title
      });
    }
  };
  
  /**
   * Get information about an element
   */
  private getElementInfo(element: HTMLElement | null): Record<string, any> {
    if (!element) return {};
    
    const rect = element.getBoundingClientRect();
    
    return {
      tagName: element.tagName.toLowerCase(),
      id: element.id || undefined,
      className: element.className || undefined,
      text: element.textContent?.slice(0, 50) || undefined,
      href: (element as HTMLAnchorElement).href || undefined,
      rect: {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
      }
    };
  }
  
  /**
   * Get the ID of a form element
   */
  private getFormId(element: HTMLElement): string | undefined {
    let parent = element.parentElement;
    
    while (parent) {
      if (parent.tagName === 'FORM') {
        return parent.id || `form-${this.generateShortId()}`;
      }
      parent = parent.parentElement;
    }
    
    return undefined;
  }
  
  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
  }
  
  /**
   * Generate a short random ID
   */
  private generateShortId(): string {
    return Math.random().toString(36).substring(2, 10);
  }
  
  /**
   * Send collected events to the server
   */
  private sendEvents(): void {
    if (this.events.length === 0) return;
    
    // Clone events and clear the queue
    const eventsToSend = [...this.events];
    this.events = [];
    
    fetch(this.options.apiUrl!, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(eventsToSend),
      // Use keepalive to ensure request completes even if page unloads
      keepalive: true
    }).catch(error => {
      console.error('Error sending tracking events:', error);
      // Add events back to the queue
      this.events = [...eventsToSend, ...this.events];
    });
  }
  
  /**
   * Start the batch timer
   */
  private startBatchTimer(): void {
    this.batchTimeout = setTimeout(() => {
      this.sendEvents();
      this.startBatchTimer();
      
      // Check for session timeout
      const inactiveTime = Date.now() - this.lastActivity;
      if (inactiveTime > this.options.sessionTimeout!) {
        this.endSession();
        this.init(); // Start a new session
      }
    }, this.options.batchInterval);
  }
  
  /**
   * Initialize WebSocket connection
   */
  private initWebSocket(): void {
    if (!this.options.websocketUrl) return;
    
    this.websocket = new WebSocket(this.options.websocketUrl);
    
    this.websocket.onopen = () => {
      console.log('Tracking WebSocket connected');
    };
    
    this.websocket.onclose = () => {
      console.log('Tracking WebSocket disconnected');
      
      // Reconnect after a delay
      setTimeout(() => {
        this.initWebSocket();
      }, 3000);
    };
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  /**
   * Create a session on the server
   */
  private createSession(): void {
    fetch('/api/tracking/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: this.sessionId,
        user_agent: navigator.userAgent,
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        language: navigator.language,
        referrer: document.referrer,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      })
    }).catch(error => {
      console.error('Error creating tracking session:', error);
    });
  }
  
  /**
   * Update session end time on the server
   */
  private updateSession(): void {
    fetch(`/api/tracking/sessions/${this.sessionId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        end_time: new Date().toISOString()
      }),
      keepalive: true
    }).catch(error => {
      console.error('Error updating tracking session:', error);
    });
  }
}

export default MouseTracker; 