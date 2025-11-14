# Budget Tracker

This project recreates Plaid's [Transactions tutorial](https://github.com/plaid/tutorial-resources/tree/main/transactions/finished) with a Python/FastAPI backend instead of the original Node.js server. The sample frontend remains a lightweight vanilla JavaScript page that mirrors the tutorial experience: launch Plaid Link, exchange the resulting public token, and show recent transactions returned from Plaid.

## Features

- **Launch Plaid Link** with a demo `demo-user` identifier
- **Exchange public tokens** for access tokens using the Plaid Python SDK
- **Fetch recent transactions** from the Transactions product and render them in a simple table
- **Stateless sample storage** that keeps access tokens in memory for local development only

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- Plaid Python SDK

### Frontend
- Vanilla JavaScript
- Plaid Link JavaScript SDK

## Project Structure

```
budget-tracker/
├── backend/          # FastAPI backend application
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # Environment configuration
│   │   ├── plaid_client.py   # Plaid client helper
│   │   ├── schemas/          # Pydantic schemas for API validation
│   │   └── storage.py        # In-memory token storage
│   ├── .env.example          # Sample backend environment configuration
│   └── requirements.txt
├── frontend/         # Vanilla JS frontend mirroring the Plaid tutorial
│   ├── config.example.js     # Sample frontend configuration
│   ├── index.html            # Main HTML page
│   ├── index.js              # Plaid Link + API interactions
│   └── styles.css            # Basic styling for the demo UI
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Plaid API credentials (Client ID, Secret, and Environment)
- A static file server for the frontend (e.g., `python -m http.server`)

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and fill in your Plaid credentials:
   ```bash
   cp .env.example .env
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

### Frontend Setup (Vanilla JS)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. (Optional) Copy the sample configuration if you need to override the backend URL:
   ```bash
   cp config.example.js config.js
   ```
   By default the frontend expects the FastAPI server at `http://localhost:8000`.

3. Serve the static files using your tool of choice. For example, with Python:
   ```bash
   python -m http.server 3000
   ```

4. Open the app in your browser at `http://localhost:3000`.

## Usage

1. Click **Connect a bank account** to start the Plaid Link flow.
2. Complete the Plaid sandbox login to authorize the sample item.
3. The backend exchanges the public token for an access token and stores it in memory.
4. Click **Refresh transactions** to re-fetch the latest transaction data. The demo always uses the `demo-user` identifier for simplicity.

## API Endpoints

- `GET /api/health` — Simple health-check endpoint
- `POST /api/create_link_token` — Creates a link token for the Plaid Link flow
- `POST /api/set_access_token` — Exchanges the public token for an access token and stores it in memory
- `GET /api/transactions?user_id=demo-user` — Retrieves the latest transactions for the specified user

## Security Notes

- Never commit your Plaid API credentials to version control.
- Keep your `.env` files local and add them to `.gitignore`.
- This sample stores tokens in memory and is suitable for local experimentation only.

## License

This is a sample application for educational use.
