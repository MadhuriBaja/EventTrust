# EventTrust

EventTrust is an evidence-based pre-registration investigation agent for unfamiliar technical, academic, and professional events.

## Current Status

EventTrust is currently in the initial scaffolding stage.

## Repository Structure

```text
EventTrust/
├── frontend/           # Next.js (App Router, TypeScript) frontend application
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── api/routes/ # API endpoints
│   │   ├── core/       # Configuration and core settings
│   │   ├── investigation/ # Investigation module scaffold
│   │   ├── models/     # Data models scaffold
│   │   ├── services/   # Services scaffold
│   │   └── main.py     # Application entrypoint
│   ├── tests/          # Backend test suite
│   ├── .env.example    # Backend environment variables template
│   └── requirements.txt# Minimal backend dependencies
├── docs/               # Documentation
├── tests/              # Root test suite
├── .gitignore          # Repository git ignore rules
├── README.md           # Project overview and status
└── PRODUCT_SPEC.md     # Product specification (source of truth)
```

## Getting Started

### Backend
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
