# Bravola Mini SaaS - Frontend

React frontend application with Vite, Redux, and Tailwind CSS.

## Features

- **React 18** - Modern React with hooks
- **Vite** - Lightning-fast build tool
- **Redux Toolkit** - State management
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Data visualization
- **Lucide Icons** - Beautiful icons

## Setup

Install dependencies
npm install

Copy environment file
cp .env.example .env

Start development server
npm run dev

text

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Project Structure

frontend/
├── src/
│ ├── api/ # API clients
│ ├── components/ # React components
│ ├── pages/ # Page components
│ ├── store/ # Redux store
│ ├── styles/ # CSS files
│ ├── utils/ # Utilities
│ ├── App.jsx # Root component
│ └── main.jsx # Entry point
├── public/ # Static assets
└── index.html # HTML template

text

## API Integration

The frontend connects to the backend API at `http://localhost:8000` by default. Update `VITE_API_URL` in `.env` to change this.

## Building for Production

npm run build

text

The optimized build will be in the `dist/` directory.