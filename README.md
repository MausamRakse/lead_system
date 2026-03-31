# MansaLeadSoftware

# Apollo Lead Extraction System

A powerful, dual-interface lead extraction tool tightly integrated with the **Apollo.io API** and **CountryStateCity API**. The system allows users to search, filter, and extract business contacts either through structured filters or a natural language AI prompt — with all data stored securely in a **Supabase PostgreSQL** database.

## 🚀 Features

- **Filter Mode**: Search for leads using specific criteria like Industry, Job Title, Company Size, Location (dynamic Country/State/City dropdowns), and custom keywords.
- **AI Prompt Mode**: Type natural language queries (e.g. *"Find founders or CEOs in AI startups with 1–200 employees"*) and let the backend automatically parse them into filters.
- **Contact Enrichment**: Unlock full contact info (emails, phone numbers, and LinkedIn profiles) on a per-lead basis to conserve Apollo API credits.
- **Supabase Database**: All extracted and unlocked leads are stored in a persistent, flat **Supabase PostgreSQL** table for fast querying and easy management.
- **Easy Export**: Download current search results as JSON or export the full lead database directly via the UI.

## 📁 Project Structure

```text
MansaLeadSoftware/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── routes/            # API route handlers
│   │   └── schemas/           # Pydantic request/response models
│   ├── utils/                 # Helper utilities (Apollo, CSC, Supabase)
│   ├── static/                # Served static frontend files
│   │   └── src/               # React source files
│   ├── run.py                 # Server startup script
│   ├── reset_db.py            # Utility to reset the Supabase DB table
│   ├── requirements.txt       # Python backend dependencies
│   ├── .env                   # Environment API Keys (not committed)
│   └── .env.example           # Example environment config
├── frontend/
│   ├── index.html             # Main HTML entry point
│   └── src/                   # React source files (JSX components)
└── README.md                  # Project documentation
```

## 🛠 Prerequisites

- Python 3.8+
- Node.js (for frontend development)
- A [Supabase](https://supabase.com/) project with a `leads` table
- An [Apollo.io API Key](https://www.apollo.io/)
- A [CountryStateCity API Key](https://countrystatecity.in/)

## ⚙️ Setup Instructions

**1. Clone the Repository**
```bash
git clone https://github.com/MausamRakse/MansaLeadSoftware.git
cd MansaLeadSoftware
```

**2. Configure Environment Variables**

Inside the `backend/` folder, create a `.env` file based on `.env.example`:
```env
APOLLO_API_KEY=your_apollo_api_key_here
CSC_API_KEY=your_country_state_city_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

**3. Install Backend Dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

Run both the backend and frontend simultaneously in separate terminals.

**Start the Backend (Terminal 1)**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Start the Frontend (Terminal 2)**
```bash
cd frontend
python3 -m http.server 3000
```

Once both are running, open your browser and navigate to:
**👉 http://localhost:3000**

## 💻 Tech Stack

- **Frontend**: React.js, Plain CSS, Axios
- **Backend**: FastAPI, Uvicorn, Python `httpx`
- **Database**: Supabase PostgreSQL (flat `leads` table)
- **APIs**: Apollo.io REST API, CountryStateCity API

---
*Built to streamline the B2B sales and lead generation pipeline.*
