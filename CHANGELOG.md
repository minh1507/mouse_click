# Changelog

## [Unreleased]

### Added
- Initial project setup
- Created CHANGELOG.md file
- Created basic directory structure for both frontend and backend
- Created frontend React + Shadcn UI configuration
- Created basic Next.js layout and home page
- Implemented basic Button component
- Created Django backend structure
- Added Django settings for development, production
- Created API views, serializers and URLs for tracking functionality
- Added WebSocket support with Channels
- Created basic tracking models
- Implemented JavaScript tracker library
- Created analytics models for heatmaps, path analysis and funnels
- Added analytics API endpoints with serializers and views
- Implemented Celery tasks for processing analytics data
- Added tracking demo page for the frontend
- Created dashboard layout with sidebar navigation
- Implemented sessions overview component with charts
- Created UI components (Card, Button, Input, Label, Tabs)
- Implemented HeatmapViewer component for visualizing interaction heatmaps
- Implemented PathAnalysis component for analyzing user navigation patterns
- Implemented FunnelAnalysis component for visualizing conversion funnels
- Added package.json with required dependencies
- Created tailwind.config.js for styling configuration
- Added tsconfig.json for TypeScript settings
- Set up Next.js configuration with API proxying
- Created home page with feature overview
- Added comprehensive README with setup instructions

### Implementation Summary
The implementation has successfully delivered a mouse behavior tracking and analysis system with the following components:

1. **Backend (Django)**
   - Session and event tracking models
   - Analytics models for heatmaps, path analysis, and funnels
   - REST API endpoints for data collection and retrieval
   - Celery tasks for batch processing of analytics data
   - WebSocket support for real-time data collection

2. **Frontend (Next.js)**
   - JavaScript tracker library for collecting mouse events
   - Dashboard layout with analytics visualizations
   - Heatmap viewer for interaction analysis
   - Path analysis for understanding user journeys
   - Funnel analysis for conversion tracking
   - Tracking demo page to showcase functionality

3. **Configuration**
   - Project structure for both frontend and backend
   - Dependencies management
   - TypeScript and Tailwind CSS configuration
   - API proxy setup for development

## Guidelines
- All changes to the project should be documented in this file
- Format: [type] - [description]
- Types: Added, Changed, Fixed, Removed, Security
- Each significant change should be added under the "Unreleased" section
- When releasing a version, create a new section with the version number and date 