/**
 * MouseTracker - Thư viện theo dõi hành vi chuột người dùng
 * Version: 1.0.0
 */

class MouseTracker {
  /**
   * Khởi tạo mouse tracker
   * @param {Object} config - Cấu hình
   * @param {string} config.apiEndpoint - Endpoint API để gửi dữ liệu
   * @param {string} config.websocketEndpoint - Endpoint WebSocket cho dữ liệu real-time
   * @param {number} config.throttleInterval - Khoảng thời gian throttle (ms)
   * @param {number} config.batchSize - Số lượng sự kiện tối đa trong một batch
   * @param {number} config.batchInterval - Khoảng thời gian gửi batch (ms)
   * @param {boolean} config.enableHeatmap - Bật/tắt heatmap
   * @param {boolean} config.enableClickTracking - Bật/tắt theo dõi click
   * @param {boolean} config.enableScrollTracking - Bật/tắt theo dõi scroll
   */
  constructor(config = {}) {
    this.config = {
      apiEndpoint: config.apiEndpoint || '/api/v1/track',
      websocketEndpoint: config.websocketEndpoint || null,
      throttleInterval: config.throttleInterval || 100,
      batchSize: config.batchSize || 50,
      batchInterval: config.batchInterval || 2000,
      enableHeatmap: config.enableHeatmap !== undefined ? config.enableHeatmap : true,
      enableClickTracking: config.enableClickTracking !== undefined ? config.enableClickTracking : true,
      enableScrollTracking: config.enableScrollTracking !== undefined ? config.enableScrollTracking : true,
    };

    // Khởi tạo buffer
    this.eventBuffer = [];
    this.lastMouseMoveEvent = null;
    this.lastScrollEvent = null;
    this.sessionId = this._generateSessionId();
    this.ws = null;

    // Trạng thái
    this.isRecording = false;
    this.isConnected = false;
    this.lastBatchSentTime = Date.now();
    
    // Đối tượng tham chiếu DOM
    this.viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };
    
    // Khởi tạo localStorage nếu cần
    this._initLocalStorage();
  }

  /**
   * Bắt đầu ghi nhận dữ liệu
   */
  start() {
    if (this.isRecording) return;
    
    this.isRecording = true;
    
    // Đăng ký các event listeners
    if (this.config.enableHeatmap) {
      document.addEventListener('mousemove', this._handleMouseMove.bind(this));
    }
    
    if (this.config.enableClickTracking) {
      document.addEventListener('click', this._handleClick.bind(this));
    }
    
    if (this.config.enableScrollTracking) {
      window.addEventListener('scroll', this._handleScroll.bind(this));
    }
    
    // Theo dõi kích thước viewport
    window.addEventListener('resize', this._handleResize.bind(this));
    
    // Theo dõi chuyển trang
    window.addEventListener('beforeunload', this._handleBeforeUnload.bind(this));
    
    // Bắt đầu WebSocket nếu được cấu hình
    if (this.config.websocketEndpoint) {
      this._initWebSocket();
    }
    
    // Bắt đầu timer gửi batch
    this._startBatchTimer();
    
    // Ghi nhận sự kiện bắt đầu phiên
    this._trackEvent('session_start', {
      url: window.location.href,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      viewport: this.viewport,
    });
    
    console.log('MouseTracker: Recording started');
  }

  /**
   * Dừng ghi nhận dữ liệu
   */
  stop() {
    if (!this.isRecording) return;
    
    this.isRecording = false;
    
    // Hủy đăng ký các event listeners
    document.removeEventListener('mousemove', this._handleMouseMove.bind(this));
    document.removeEventListener('click', this._handleClick.bind(this));
    window.removeEventListener('scroll', this._handleScroll.bind(this));
    window.removeEventListener('resize', this._handleResize.bind(this));
    window.removeEventListener('beforeunload', this._handleBeforeUnload.bind(this));
    
    // Đóng WebSocket
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    // Gửi batch cuối cùng
    this._sendBatch();
    
    console.log('MouseTracker: Recording stopped');
  }

  /**
   * Xử lý sự kiện di chuyển chuột
   * @private
   * @param {MouseEvent} event - Sự kiện di chuyển chuột
   */
  _handleMouseMove(event) {
    if (!this.isRecording) return;
    
    const now = Date.now();
    
    // Áp dụng throttling
    if (this.lastMouseMoveEvent && (now - this.lastMouseMoveEvent.timestamp < this.config.throttleInterval)) {
      return;
    }
    
    // Lưu lại thời điểm cuối cùng
    this.lastMouseMoveEvent = {
      timestamp: now,
    };
    
    // Ghi nhận sự kiện
    this._trackEvent('mouse_move', {
      x: event.clientX,
      y: event.clientY,
      pageX: event.pageX,
      pageY: event.pageY,
      relativeX: event.clientX / this.viewport.width,
      relativeY: event.clientY / this.viewport.height,
    });
  }

  /**
   * Xử lý sự kiện click chuột
   * @private
   * @param {MouseEvent} event - Sự kiện click chuột
   */
  _handleClick(event) {
    if (!this.isRecording) return;
    
    // Xác định element được click
    const element = event.target;
    const elementInfo = this._getElementInfo(element);
    
    // Ghi nhận sự kiện
    this._trackEvent('mouse_click', {
      x: event.clientX,
      y: event.clientY,
      pageX: event.pageX,
      pageY: event.pageY,
      relativeX: event.clientX / this.viewport.width,
      relativeY: event.clientY / this.viewport.height,
      button: event.button,
      element: elementInfo,
    });
  }

  /**
   * Xử lý sự kiện scroll
   * @private
   * @param {Event} event - Sự kiện scroll
   */
  _handleScroll(event) {
    if (!this.isRecording) return;
    
    const now = Date.now();
    
    // Áp dụng throttling
    if (this.lastScrollEvent && (now - this.lastScrollEvent.timestamp < this.config.throttleInterval)) {
      return;
    }
    
    // Lưu lại thời điểm cuối cùng
    this.lastScrollEvent = {
      timestamp: now,
    };
    
    // Ghi nhận sự kiện
    this._trackEvent('scroll', {
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      maxScrollX: document.documentElement.scrollWidth - this.viewport.width,
      maxScrollY: document.documentElement.scrollHeight - this.viewport.height,
      relativeScrollX: document.documentElement.scrollWidth > this.viewport.width
        ? window.scrollX / (document.documentElement.scrollWidth - this.viewport.width)
        : 0,
      relativeScrollY: document.documentElement.scrollHeight > this.viewport.height
        ? window.scrollY / (document.documentElement.scrollHeight - this.viewport.height)
        : 0,
    });
  }

  /**
   * Xử lý sự kiện thay đổi kích thước viewport
   * @private
   * @param {Event} event - Sự kiện resize
   */
  _handleResize(event) {
    if (!this.isRecording) return;
    
    this.viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };
    
    // Ghi nhận sự kiện
    this._trackEvent('viewport_resize', {
      width: this.viewport.width,
      height: this.viewport.height,
    });
  }

  /**
   * Xử lý sự kiện trước khi rời trang
   * @private
   * @param {Event} event - Sự kiện beforeunload
   */
  _handleBeforeUnload(event) {
    if (!this.isRecording) return;
    
    // Ghi nhận sự kiện kết thúc phiên
    this._trackEvent('session_end', {
      duration: Date.now() - this.sessionStartTime,
    });
    
    // Gửi batch cuối cùng
    this._sendBatch(true);
  }

  /**
   * Ghi nhận một sự kiện vào buffer
   * @private
   * @param {string} eventType - Loại sự kiện
   * @param {Object} eventData - Dữ liệu sự kiện
   */
  _trackEvent(eventType, eventData) {
    if (!this.isRecording) return;
    
    const event = {
      type: eventType,
      timestamp: Date.now(),
      url: window.location.href,
      sessionId: this.sessionId,
      data: eventData,
    };
    
    // Thêm vào buffer
    this.eventBuffer.push(event);
    
    // Gửi qua WebSocket nếu kết nối
    if (this.ws && this.isConnected && ['mouse_click', 'session_start', 'session_end'].includes(eventType)) {
      this._sendWebSocketEvent(event);
    }
    
    // Gửi batch nếu đủ kích thước
    if (this.eventBuffer.length >= this.config.batchSize) {
      this._sendBatch();
    }
  }

  /**
   * Bắt đầu timer gửi batch
   * @private
   */
  _startBatchTimer() {
    setInterval(() => {
      const now = Date.now();
      
      // Kiểm tra thời gian từ lần gửi cuối
      if (now - this.lastBatchSentTime >= this.config.batchInterval && this.eventBuffer.length > 0) {
        this._sendBatch();
      }
      
      // Khôi phục dữ liệu từ localStorage nếu cần
      this._recoverFromLocalStorage();
    }, this.config.batchInterval);
  }

  /**
   * Gửi batch dữ liệu lên server
   * @private
   * @param {boolean} sync - Gửi đồng bộ (dùng khi beforeunload)
   */
  _sendBatch(sync = false) {
    if (this.eventBuffer.length === 0) return;
    
    // Chuẩn bị batch để gửi
    const batch = {
      sessionId: this.sessionId,
      events: [...this.eventBuffer],
      metadata: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        timestamp: Date.now(),
      },
    };
    
    // Xóa buffer hiện tại
    this.eventBuffer = [];
    this.lastBatchSentTime = Date.now();
    
    // Chuyển đổi thành JSON
    const batchData = JSON.stringify(batch);
    
    // Lưu vào localStorage để đề phòng lỗi
    if (!sync) {
      this._saveToLocalStorage(batchData);
    }
    
    // Gửi lên server
    const xhr = new XMLHttpRequest();
    xhr.open('POST', this.config.apiEndpoint, !sync);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          // Xóa khỏi localStorage nếu gửi thành công
          this._removeFromLocalStorage(batchData);
        } else {
          console.error('MouseTracker: Failed to send batch', xhr.status, xhr.responseText);
        }
      }
    };
    
    xhr.send(batchData);
  }

  /**
   * Khởi tạo WebSocket
   * @private
   */
  _initWebSocket() {
    if (!this.config.websocketEndpoint) return;
    
    this.ws = new WebSocket(this.config.websocketEndpoint);
    
    this.ws.onopen = () => {
      this.isConnected = true;
      console.log('MouseTracker: WebSocket connected');
    };
    
    this.ws.onclose = () => {
      this.isConnected = false;
      console.log('MouseTracker: WebSocket closed');
      
      // Thử kết nối lại sau 5 giây
      setTimeout(() => {
        if (this.isRecording) {
          this._initWebSocket();
        }
      }, 5000);
    };
    
    this.ws.onerror = (error) => {
      console.error('MouseTracker: WebSocket error', error);
    };
  }

  /**
   * Gửi sự kiện qua WebSocket
   * @private
   * @param {Object} event - Sự kiện cần gửi
   */
  _sendWebSocketEvent(event) {
    if (!this.ws || !this.isConnected) return;
    
    try {
      this.ws.send(JSON.stringify(event));
    } catch (error) {
      console.error('MouseTracker: Failed to send WebSocket event', error);
    }
  }

  /**
   * Lấy thông tin của element
   * @private
   * @param {HTMLElement} element - Element cần lấy thông tin
   * @returns {Object} Thông tin element
   */
  _getElementInfo(element) {
    if (!element) return null;
    
    // Tránh lấy quá nhiều thông tin
    const maxDepth = 3;
    
    const getElementPath = (el, depth = 0) => {
      if (!el || !el.tagName || depth > maxDepth) return '';
      
      let path = el.tagName.toLowerCase();
      
      if (el.id) {
        path += `#${el.id}`;
      } else if (el.className && typeof el.className === 'string') {
        path += `.${el.className.trim().replace(/\s+/g, '.')}`;
      }
      
      return el.parentElement
        ? `${getElementPath(el.parentElement, depth + 1)} > ${path}`
        : path;
    };
    
    return {
      tag: element.tagName.toLowerCase(),
      id: element.id || null,
      class: element.className || null,
      text: element.textContent ? element.textContent.substring(0, 100) : null,
      path: getElementPath(element),
      attributes: {
        href: element.getAttribute('href') || null,
        src: element.getAttribute('src') || null,
        alt: element.getAttribute('alt') || null,
        title: element.getAttribute('title') || null,
      },
    };
  }

  /**
   * Tạo sessionId ngẫu nhiên
   * @private
   * @returns {string} sessionId
   */
  _generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  /**
   * Khởi tạo localStorage
   * @private
   */
  _initLocalStorage() {
    this.localStorageKey = 'mousetracker_events';
    
    try {
      if (!localStorage.getItem(this.localStorageKey)) {
        localStorage.setItem(this.localStorageKey, JSON.stringify([]));
      }
    } catch (error) {
      console.error('MouseTracker: Failed to initialize localStorage', error);
    }
  }

  /**
   * Lưu batch vào localStorage
   * @private
   * @param {string} batchData - Dữ liệu batch dạng JSON
   */
  _saveToLocalStorage(batchData) {
    try {
      const storedEvents = JSON.parse(localStorage.getItem(this.localStorageKey) || '[]');
      storedEvents.push(batchData);
      
      // Giới hạn số lượng batch được lưu
      if (storedEvents.length > 10) {
        storedEvents.shift();
      }
      
      localStorage.setItem(this.localStorageKey, JSON.stringify(storedEvents));
    } catch (error) {
      console.error('MouseTracker: Failed to save to localStorage', error);
    }
  }

  /**
   * Xóa batch khỏi localStorage
   * @private
   * @param {string} batchData - Dữ liệu batch dạng JSON
   */
  _removeFromLocalStorage(batchData) {
    try {
      const storedEvents = JSON.parse(localStorage.getItem(this.localStorageKey) || '[]');
      const index = storedEvents.indexOf(batchData);
      
      if (index !== -1) {
        storedEvents.splice(index, 1);
        localStorage.setItem(this.localStorageKey, JSON.stringify(storedEvents));
      }
    } catch (error) {
      console.error('MouseTracker: Failed to remove from localStorage', error);
    }
  }

  /**
   * Khôi phục dữ liệu từ localStorage
   * @private
   */
  _recoverFromLocalStorage() {
    try {
      const storedEvents = JSON.parse(localStorage.getItem(this.localStorageKey) || '[]');
      
      if (storedEvents.length === 0) return;
      
      // Gửi lại các batch đã lưu
      storedEvents.forEach((batchData) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', this.config.apiEndpoint, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4 && xhr.status === 200) {
            // Xóa khỏi localStorage nếu gửi thành công
            this._removeFromLocalStorage(batchData);
          }
        };
        
        xhr.send(batchData);
      });
    } catch (error) {
      console.error('MouseTracker: Failed to recover from localStorage', error);
    }
  }
}

// Export cho Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MouseTracker;
}

// Export cho browser
if (typeof window !== 'undefined') {
  window.MouseTracker = MouseTracker;
}

// Ví dụ sử dụng:
/*
const tracker = new MouseTracker({
  apiEndpoint: 'https://api.example.com/track',
  websocketEndpoint: 'wss://api.example.com/stream',
  throttleInterval: 100,
  batchSize: 50,
  batchInterval: 2000,
});

// Bắt đầu ghi nhận dữ liệu
tracker.start();

// Dừng ghi nhận dữ liệu
// tracker.stop();
*/ 