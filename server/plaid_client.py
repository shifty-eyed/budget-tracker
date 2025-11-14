"""Plaid client configuration"""
import os
import plaid
from plaid.api import plaid_api

# Get environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

# Map environment string to Plaid environment
if PLAID_ENV == "sandbox":
    host = plaid.Environment.Sandbox
elif PLAID_ENV == "development":
    host = plaid.Environment.Development
elif PLAID_ENV == "production":
    host = plaid.Environment.Production
else:
    host = plaid.Environment.Sandbox

# Set up Plaid configuration
configuration = plaid.Configuration(
    host=host,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)
