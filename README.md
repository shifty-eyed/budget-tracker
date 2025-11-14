# Budget Tracker - Plaid Transactions App

A personal finance tracker that integrates with Plaid to fetch and display your bank transactions. This application demonstrates how to use Plaid's Transactions API to build a simple budget tracking application.

**This is a Python/FastAPI implementation** of the original Node.js tutorial from [Plaid's tutorial-resources repository](https://github.com/plaid/tutorial-resources/tree/main/transactions/finished).

## Features

- 🏦 Connect multiple bank accounts via Plaid Link
- 💰 View all transactions from connected accounts
- 🔄 Sync transactions using Plaid's Transactions Sync API
- 📊 Categorized transaction display
- 🔐 Simple user authentication (demo purposes only)
- 🪝 Webhook support for real-time updates

## Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **aiosqlite**: Async SQLite database operations
- **SQLite**: Lightweight, file-based database for local data storage
- **Plaid Python SDK**: Financial services API for connecting bank accounts

### Frontend
- **HTML/CSS**: Bootstrap 5 for styling
- **JavaScript (ES6)**: Vanilla JavaScript with modules
- **Plaid Link**: Bank connection UI component

## Project Structure

```
budget-tracker/
├── server/
│   ├── __init__.py
│   ├── server.py              # Main FastAPI application
│   ├── webhook_server.py      # Webhook handler
│   ├── db.py                  # Database operations
│   ├── plaid_client.py        # Plaid client configuration
│   ├── simple_transaction.py  # Transaction data model
│   ├── utils.py               # Utility functions
│   └── routes/
│       ├── __init__.py
│       ├── users.py           # User management endpoints
│       ├── tokens.py          # Plaid Link token endpoints
│       ├── banks.py           # Bank connection endpoints
│       ├── transactions.py    # Transaction sync endpoints
│       └── debug.py           # Debug/testing endpoints
├── public/
│   ├── index.html             # Main frontend page
│   └── js/
│       ├── client.js          # Main client logic
│       ├── link.js            # Plaid Link integration
│       ├── signin.js          # Authentication
│       └── utils.js           # Frontend utilities
├── database/
│   └── appdata.db             # SQLite database (auto-created)
├── .env.template              # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

1. Python 3.8 or higher
2. A Plaid account (free sandbox account available)
3. Plaid API credentials (Client ID and Secret)

## Setup Instructions

### 1. Get Plaid API Keys

1. Sign up for a free account at [Plaid Dashboard](https://dashboard.plaid.com/)
2. Get your `client_id` and `sandbox` secret from the dashboard

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your Plaid credentials
# PLAID_CLIENT_ID=your_client_id_here
# PLAID_SECRET=your_sandbox_secret_here
# PLAID_ENV=sandbox
```

### 4. Run the Application

```bash
# Start the main server
python -m uvicorn server.server:app --reload --port 8000
```

The application will be available at `http://localhost:8000`

### 5. Optional: Run Webhook Server

If you want to test webhooks (for automatic transaction updates):

```bash
# In a separate terminal
python -m uvicorn server.webhook_server:webhook_app --reload --port 8001
```

To expose webhooks to Plaid (for testing), you can use ngrok:

```bash
# Install ngrok: https://ngrok.com/
ngrok http 8001
```

Then update your `.env` file with the ngrok URL:
```
WEBHOOK_URL=https://your-ngrok-url.ngrok.io/server/receive_webhook
```

## Usage

1. **Create an Account**: Enter a username and click "Create account!"
2. **Connect a Bank**: Click "Connect my bank!" and use Plaid Link to connect a bank account
   - In sandbox mode, use the test credentials provided by Plaid
3. **View Transactions**: Your transactions will automatically sync and display
4. **Sync Transactions**: Click "Server refresh" to manually sync new transactions
5. **Disconnect Banks**: Select a bank from the dropdown and click "Stop using this bank"

## Sandbox Testing

In sandbox mode, you can use Plaid's test credentials:
- Username: `user_good`
- Password: `pass_good`

These will give you access to test accounts with sample transaction data.

## API Endpoints

### Users
- `POST /server/users/create` - Create a new user
- `GET /server/users/list` - Get all users
- `POST /server/users/sign_in` - Sign in
- `POST /server/users/sign_out` - Sign out
- `GET /server/users/get_my_info` - Get current user info

### Plaid Tokens
- `POST /server/tokens/generate_link_token` - Generate Plaid Link token
- `POST /server/tokens/exchange_public_token` - Exchange public token for access token

### Banks
- `GET /server/banks/list` - List connected banks
- `POST /server/banks/deactivate` - Disconnect a bank

### Transactions
- `POST /server/transactions/sync` - Sync transactions from Plaid
- `GET /server/transactions/list` - Get user transactions

### Debug
- `POST /server/debug/run` - Run custom debug code
- `POST /server/debug/generate_webhook` - Trigger test webhook (sandbox only)

## Database Schema

The application uses SQLite with the following tables:

- **users**: User accounts
- **items**: Bank connections (Plaid items)
- **accounts**: Bank accounts
- **transactions**: Transaction records

## Troubleshooting

**"Database is locked" error:**
- Make sure only one instance of the server is running
- Delete `database/appdata.db` and restart

**Plaid API errors:**
- Verify your credentials in `.env`
- Check that you're using the correct environment (sandbox/production)
- Ensure your Plaid account has access to the Transactions product

**Transactions not syncing:**
- Click "Server refresh" to manually trigger sync
- Check browser console for JavaScript errors
- Verify webhook URL is accessible (if using webhooks)

## Differences from Node.js Version

This Python/FastAPI implementation maintains the same functionality as the original Node.js version while adapting to Python best practices:

- **Framework**: FastAPI instead of Express.js
- **Database**: aiosqlite for async operations instead of callback-based sqlite
- **Type Safety**: Pydantic models for request/response validation
- **Async/Await**: Native Python async throughout
- **Structure**: Python module organization

## Security Notes

⚠️ **This is a demonstration application and should NOT be used in production without significant security improvements:**

- No password authentication (users just select their ID)
- Cookies are used for simple session management
- No input validation on some endpoints
- Plaid access tokens stored in plain text in database
- No rate limiting
- No HTTPS enforcement

For production use, implement:
- Proper authentication (OAuth, JWT, etc.)
- Password hashing (bcrypt, argon2, etc.)
- Encrypted storage for sensitive data
- Rate limiting and request validation
- HTTPS/TLS
- CSRF protection
- Security headers

## Learn More

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Original Node.js Tutorial](https://github.com/plaid/tutorial-resources/tree/main/transactions)

## License

MIT

## Contributing

This is a demonstration project. Feel free to fork and modify for your own use!

