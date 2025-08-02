from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .database import init_db, close_db
from .api import (
    auth_router,
    users_router,
    accounts_router,
    transactions_router,
    portfolios_router,
    balances_router
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Personal Finance Dashboard API")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Personal Finance Dashboard API")
    await close_db()

app = FastAPI(
    title="Personal Finance Dashboard API",
    description="A modern API for personal finance tracking and investment management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(portfolios_router)
app.include_router(balances_router)

@app.get("/")
async def root():
    return {"message": "Personal Finance Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance-dashboard-api"}

@app.get("/metrics")
async def metrics():
    # TODO: Implement business metrics endpoint
    return {
        "total_accounts": 0,
        "total_portfolio_value": 0,
        "last_sync": None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
