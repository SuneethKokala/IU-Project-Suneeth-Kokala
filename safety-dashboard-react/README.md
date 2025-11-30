# Safety Monitoring Dashboard - React Frontend

This is the React.js frontend for the Automated Industrial Safety Management System.

## Features

- **Modern React UI** - Clean, responsive interface
- **Real-time PPE Detection** - Upload images for instant analysis
- **Employee Management** - Add, view, and delete employees
- **Violation Tracking** - View and manage safety violations
- **Interactive 3D Background** - Three.js animated background
- **Excel Export** - Download violation reports

## Tech Stack

- **React 18** - Frontend framework
- **Three.js** - 3D graphics and animations
- **Axios** - HTTP client for API calls
- **Font Awesome** - Icons and UI elements

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python backend running on port 3001

### Installation

1. Install dependencies:
```bash
npm install --legacy-peer-deps
```

2. Start the development server:
```bash
npm start
```

3. Or run both frontend and backend together:
```bash
npm run dev
```

### Available Scripts

- `npm start` - Start React development server (port 3000)
- `npm run build` - Build for production
- `npm run start-backend` - Start Python backend
- `npm run dev` - Run both frontend and backend concurrently

## API Endpoints

The React app communicates with the Python backend on `http://localhost:3001`:

- `POST /login` - User authentication
- `GET /api/violations` - Get violation history
- `POST /api/mark_notified` - Mark violation as notified
- `POST /api/upload_image` - Upload image for PPE detection
- `GET /api/employees` - Get employee list
- `POST /api/add_employee` - Add new employee
- `POST /api/delete_employee` - Delete employee
- `GET /api/export_excel` - Export violations to Excel

## Components

- **App.js** - Main application with routing
- **Login.js** - Authentication component
- **Dashboard.js** - Main dashboard view
- **Employees.js** - Employee management
- **ViolationHistory.js** - Violation display and management
- **ImageUpload.js** - PPE detection image upload
- **Stats.js** - Statistics cards
- **ThreeBackground.js** - 3D animated background

## Default Login

- Username: `supervisor`
- Password: `admin123`

## Build for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files.