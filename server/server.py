"""Main FastAPI server"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from server.routes import users, tokens, banks, transactions, debug
from server import db

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Budget Tracker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/server/users", tags=["users"])
app.include_router(tokens.router, prefix="/server/tokens", tags=["tokens"])
app.include_router(banks.router, prefix="/server/banks", tags=["banks"])
app.include_router(transactions.router, prefix="/server/transactions", tags=["transactions"])
app.include_router(debug.router, prefix="/server/debug", tags=["debug"])

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await db.init_db()
    print("Database initialized")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"Error: {exc}")

    # Check if it's a Plaid error
    if hasattr(exc, 'body'):
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )

    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
