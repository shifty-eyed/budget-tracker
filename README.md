# Budget Tracker

A personal budget tracking web application similar to Intuit Mint, designed to help you manage your finances by connecting to your bank accounts and credit cards, automatically fetching transactions, and providing insights into your spending habits.

## Features

- **Bank Account Integration**: Connect multiple bank accounts and credit card accounts via Plaid API
- **Automatic Transaction Fetching**: Automatically retrieve and store all transactions from connected accounts
- **Transaction Management**: View, categorize, and manage all your financial transactions in one place
- **Budget Tracking**: Monitor your spending and track your budget across different categories
- **Secure Data Storage**: All transaction data is stored locally in a SQLite database

## Tech Stack

### Backend
- **Python 3.x**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **SQLite**: Lightweight, file-based database for local data storage
- **Plaid API**: Financial services API for connecting bank accounts

### Frontend
- **Vue.js**: Progressive JavaScript framework for building user interfaces

## Project Structure

```
budget-tracker/
├── backend/          # FastAPI backend application
│   ├── app/
│   │   ├── main.py   # FastAPI application entry point
│   │   ├── models/   # SQLAlchemy database models
│   │   ├── schemas/  # Pydantic schemas for API validation
│   │   ├── api/      # API route handlers
│   │   └── services/ # Business logic and Plaid integration
│   ├── requirements.txt
│   └── database.db   # SQLite database file
├── frontend/         # Vue.js frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   └── main.js
│   └── package.json
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Node.js 16.x or higher
- npm or yarn package manager
- Plaid API credentials (Client ID, Secret, and Environment)

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with your Plaid credentials:
   ```
   PLAID_CLIENT_ID=your_client_id
   PLAID_SECRET=your_secret
   PLAID_ENV=sandbox  # or 'development' or 'production'
   DATABASE_URL=sqlite:///./database.db
   ```

5. Run database migrations (if applicable):
   ```bash
   alembic upgrade head
   ```

6. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation will be available at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the frontend directory:
   ```
   VUE_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run serve
   ```

   The frontend will be available at `http://localhost:8080`

## Usage

1. **Connect Bank Accounts**: Use the Plaid Link flow to securely connect your bank accounts and credit cards
2. **Fetch Transactions**: The app will automatically fetch and store all transactions from connected accounts
3. **View Transactions**: Browse and filter your transactions by date, category, or account
4. **Track Budget**: Set budget limits and monitor your spending across different categories

## API Endpoints

- `GET /api/accounts` - List all connected accounts
- `POST /api/accounts/link` - Initiate Plaid Link flow
- `GET /api/transactions` - Retrieve all transactions
- `POST /api/transactions/sync` - Sync transactions from Plaid
- `GET /api/transactions/{id}` - Get specific transaction details

## Database Schema

The SQLite database stores:
- **Accounts**: Connected bank and credit card accounts
- **Transactions**: All financial transactions with details (amount, date, category, description)
- **Categories**: Transaction categories for budgeting

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm run test:unit
```

### Code Style

Backend uses Black for code formatting:
```bash
cd backend
black .
```

Frontend uses ESLint:
```bash
cd frontend
npm run lint
```

## Security Notes

- Never commit your Plaid API credentials to version control
- Keep your `.env` files local and add them to `.gitignore`
- Use environment variables for all sensitive configuration
- The SQLite database contains sensitive financial data - ensure proper file permissions

## License

This is a personal project for individual use.

## Contributing

This is a personal budget tracking application. Contributions and suggestions are welcome!

## Acknowledgments

- [Plaid](https://plaid.com/) for providing the financial services API
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Vue.js](https://vuejs.org/) for the progressive JavaScript framework

