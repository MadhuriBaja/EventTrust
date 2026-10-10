# EventTrust — Trust, Backed by Evidence

EventTrust is an evidence-first event research platform that helps people investigate events, discover supporting sources, and review available evidence before deciding whether to trust an event.

Rather than making unsupported claims that an event is legitimate or fraudulent, EventTrust organizes available information into a research report with source-linked findings, an evidence assessment, and transparent research limitations.

**Research supports your decision; it does not guarantee an event's legitimacy.**

## Overview

Online events, workshops, meetups, and community gatherings can be difficult to evaluate when their organizers, venues, registration pages, or supporting information are unfamiliar.

EventTrust provides a structured investigation workflow that helps users:

* Investigate an event using its name, registration URL, or both.
* Gather event details and supporting research.
* Review findings with links to their original sources.
* Understand the available evidence and its relevance.
* Identify missing information and research limitations.
* Make more informed decisions without treating missing evidence as proof of fraud.

## Key Features

### 1. Event Investigation

Start an investigation using an event name, an event registration URL, or both.

EventTrust creates an investigation record containing the event details and the research results available to the system.

### 2. Evidence-Backed Research

The backend uses a search service to discover potentially relevant information about an event.

Research findings are intended to help users investigate details such as:

* Event announcements and registration pages.
* Organizer and community information.
* Venue and event details.
* Independent references and corroborating sources.
* Information that may require additional verification.

The availability and quality of these findings depend on search results, source accessibility, and the information supplied by the user.

### 3. Source-Linked Findings

Findings include source information so users can inspect the original material and assess its context.

EventTrust encourages users to review the source itself rather than relying exclusively on an automated summary or assessment.

### 4. Evidence Assessment

EventTrust presents an assessment based on the evidence available to the investigation.

An **Insufficient Evidence** result means that the available information does not support a sufficiently confident assessment. It does not automatically mean that the event is fraudulent.

Likewise, positive evidence does not guarantee that an event is safe or legitimate.

### 5. Transparent Research Limitations

The report communicates evidence gaps and research limitations so users can understand what the system could and could not establish.

Unavailable search results, inaccessible pages, or missing details should be treated as limitations—not as conclusive evidence of wrongdoing.

### 6. Investigation Reports

Each investigation brings together the available event details, assessment, source-linked findings, and research limitations in one interface.

Users can return to the report and review the available information before making a decision.

## How It Works

1. **Identify the event:** Enter an event name, registration URL, or both.
2. **Gather evidence:** The backend collects available event information and searches for potentially relevant sources.
3. **Review findings:** Inspect returned findings, source links, and their original context.
4. **Evaluate the assessment:** Review what the available evidence supports and what remains uncertain.
5. **Make an informed decision:** Verify important details directly with the organizer, venue, or official source.

## Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI
* Pydantic Settings
* HTTPX
* Beautiful Soup
* SerpApi for web search

### Deployment

* Vercel for the frontend
* Render for the backend

### Testing

* Pytest
* HTTPX test client
* TypeScript type checking
* Next.js production build

## Project Structure

```text
EventTrust/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Procfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   ├── lib/
│   │   └── api.ts
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

The exact contents of individual directories may evolve as the project develops.

## Getting Started

### Prerequisites

Install the following:

* Node.js and npm
* Python 3.10 or later
* Git
* A SerpApi API key for live web-search functionality

### 1. Clone the Repository

```bash
git clone https://github.com/MadhuriBaja/EventTrust.git
cd EventTrust
```

### 2. Set Up the Backend

Open a terminal in the project root.

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and configure the required values:

```env
SERPAPI_API_KEY=your_serpapi_api_key_here
FRONTEND_ORIGIN=http://localhost:3000
```

Replace the placeholder with your own SerpApi key. Keep this file private and never commit it to GitHub.

Start the backend:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend should be available at:

* API root: http://localhost:8000/
* Health check: http://localhost:8000/health
* API health check: http://localhost:8000/api/health
* Interactive API documentation: http://localhost:8000/docs

The health endpoints help confirm that the backend is running. They do not, by themselves, verify that live search is working.

### 3. Set Up the Frontend

Open a second terminal in the project root:

```powershell
cd frontend
npm install
```

Create `frontend/.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```powershell
npm run dev
```

Open:

http://localhost:3000

The frontend sends API requests to the backend URL configured through `NEXT_PUBLIC_API_URL`.

Restart the frontend development server after changing environment variables.

## Configuration

### Backend Environment Variables

| Variable          | Purpose                                                     |
| ----------------- | ----------------------------------------------------------- |
| `SERPAPI_API_KEY` | API key used for web-search requests                        |
| `FRONTEND_ORIGIN` | Frontend origin permitted by the backend CORS configuration |

### Frontend Environment Variables

| Variable              | Purpose                         |
| --------------------- | ------------------------------- |
| `NEXT_PUBLIC_API_URL` | Base URL of the FastAPI backend |

Only public configuration belongs in frontend environment variables. Never expose private API keys or secrets through variables prefixed with `NEXT_PUBLIC_`.

## Deployment

### Frontend — Vercel

The production frontend is deployed on Vercel:

https://eventtrust.vercel.app/

Recommended configuration:

* Root directory: `frontend`
* Framework preset: Next.js
* Environment variable: `NEXT_PUBLIC_API_URL=https://eventtrust-backend.onrender.com`

After updating environment variables, redeploy the frontend so the production build uses the correct API URL.

### Backend — Render

The production backend is deployed on Render:

https://eventtrust-backend.onrender.com/

Recommended configuration:

* Root directory: `backend`
* Build command: `pip install -r requirements.txt`
* Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Configure the following backend environment variables in Render:

* `SERPAPI_API_KEY` — your private search API key.
* `FRONTEND_ORIGIN` — `https://eventtrust.vercel.app`

The backend must allow requests from the deployed frontend origin.

Render's free service may take time to wake up after inactivity. A delayed initial request does not necessarily mean the service is broken.

### Verify the Deployment

Check the backend health endpoint:

https://eventtrust-backend.onrender.com/health

A healthy response should resemble:

```json
{
  "status": "ok"
}
```

Then open the frontend and start a new investigation.

A successful health check confirms that the backend is responding, but the full investigation workflow must also be tested to verify API connectivity, CORS configuration, and search functionality.

## Testing

### Backend Tests

From the backend directory, activate the virtual environment and run:

```powershell
python -m pytest -q
```

### Frontend Type Checking

From the frontend directory:

```powershell
npx tsc --noEmit
```

### Frontend Production Build

```powershell
npm run build
```

Run these checks after making relevant changes. A successful build does not guarantee that external APIs or production environment variables are configured correctly.

## Troubleshooting

### Failed to Fetch

If the frontend displays `Failed to fetch`:

1. Confirm that the backend health endpoint responds.
2. Check `NEXT_PUBLIC_API_URL` in the Vercel project settings.
3. Confirm that `FRONTEND_ORIGIN` matches the deployed frontend origin.
4. Check the browser's developer tools for network and CORS errors.
5. Inspect Render logs for errors during the investigation request.
6. Redeploy after changing production environment variables when required.

### Investigation Returns Zero Findings

An investigation may return event details but no research findings.

Possible causes include:

* The search API returned no relevant results.
* The API key is invalid or missing.
* The search provider rejected the request or exhausted its quota.
* A research-service error was handled without returning findings.
* Results were filtered out or failed validation.
* Search coverage was insufficient for the supplied event.

Inspect the backend logs for the specific request before changing the implementation. A completed investigation does not necessarily mean that useful external evidence was found.

### CORS Errors

Verify that the frontend's deployed origin exactly matches `FRONTEND_ORIGIN`, including the protocol and hostname.

For the current production deployment, use:

```env
FRONTEND_ORIGIN=https://eventtrust.vercel.app
```

Do not add a trailing slash unless the backend's CORS implementation explicitly expects it.

### Render Deployment Errors

Check the build output, dependency installation, Python runtime, start command, and environment variables in the Render dashboard.

A `HEAD /` response with status `405 Method Not Allowed` does not necessarily indicate a failed deployment if the application does not implement a HEAD handler. Verify the health endpoint and actual GET requests.

## Responsible Use

EventTrust is a research-assistance tool, not a definitive fraud detector or a guarantee of event safety.

* Search results may be incomplete, outdated, or inaccurate.
* Source links should be inspected in their original context.
* Automated assessments should not replace independent judgment.
* Missing evidence is not proof of fraud.
* Positive evidence is not proof that an event is safe.
* Important event details should be confirmed directly with the organizer or venue.
* Research limitations should be considered before making consequential decisions.

EventTrust aims to make event evaluation more transparent by showing users the evidence available to them and the uncertainties that remain.

## Future Improvements

Potential improvements include:

* Better corroboration across independent sources.
* Clearer relevance and credibility indicators for individual findings.
* More detailed explanations for evidence assessments.
* Stronger detection and reporting of search failures.
* Improved handling of empty or partially available research results.
* Investigation history and report retrieval.
* Additional source types and research providers.
* More comprehensive integration and deployment tests.

These are possible future enhancements, not claims that every feature is already implemented.

## License

No license has been specified yet. Until a license is added to the repository, reuse and redistribution are subject to applicable copyright law.

## Author

**Madhuri Baja**

GitHub: https://github.com/MadhuriBaja

---

**EventTrust — Trust, backed by evidence.**

Investigate events. Review the sources. Decide with greater confidence.
