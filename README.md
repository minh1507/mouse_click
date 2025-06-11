# Mouse Tracking Analysis

A comprehensive solution for tracking and analyzing mouse behavior on websites. This project provides tools for collecting mouse events (movements, clicks, scrolls) and visualizing the data with heatmaps, path analysis, and funnel visualizations.

## Features

- **Mouse Tracking**: Track mouse movements, clicks, scrolls, and form interactions
- **Heatmap Analysis**: Visualize user interaction patterns with heatmaps
- **Path Analysis**: Analyze user navigation paths across your site
- **Funnel Analysis**: Track conversion paths and identify drop-off points
- **Real-time Data Collection**: Collect data in real-time using WebSockets
- **Batch Processing**: Process large amounts of data efficiently using Celery

## Tech Stack

### Frontend
- **Next.js**: React framework for the web application
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn UI**: Accessible and customizable UI components
- **Recharts**: Charting library for data visualization

### Backend
- **Django**: Python web framework
- **Django REST Framework**: RESTful API framework
- **Channels**: WebSocket support for real-time data collection
- **Celery**: Distributed task queue for batch processing
- **MongoDB**: NoSQL database for data storage

## Project Structure

```
.
├── backend/
│   ├── apps/
│   │   ├── analytics/       # Analytics models, views, and tasks
│   │   ├── api/             # API routes and views
│   │   └── tracking/        # Tracking models and websocket consumers
│   ├── config/              # Django settings and configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   ├── components/      # React components
│   │   │   ├── dashboard/   # Dashboard UI components
│   │   │   ├── tracking/    # Tracking-related components
│   │   │   └── ui/          # Reusable UI components
│   │   └── lib/             # Utility functions and tracker library
│   ├── package.json         # JavaScript dependencies
│   └── tailwind.config.js   # Tailwind CSS configuration
├── CHANGELOG.md             # Project changelog
└── README.md                # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- MongoDB

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Adding Tracking to Your Website

1. Import the tracker library:
   ```javascript
   import MouseTracker from '@/lib/tracker';
   ```

2. Initialize the tracker:
   ```javascript
   const tracker = new MouseTracker({
     apiUrl: 'https://your-api-url.com/api/tracking/events',
     trackMouseMove: true,
     trackMouseClick: true,
     trackScroll: true,
     sampleRate: 0.1  // Sample 10% of mouse move events
   });
   
   tracker.init();
   ```

3. View the collected data in the dashboard.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Database Configuration

The application uses MongoDB as the database backend.

### MongoDB Setup

1. Install MongoDB on your system if you haven't already
2. Start the MongoDB service
3. The application connects to MongoDB at `localhost:27017` by default
4. No authentication is required for development setup 