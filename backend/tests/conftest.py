import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token
from app.database import get_db
from app.main import app
from app.models import Base

# Test database URL - use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Set up test database and create tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Generator:
    """Create a test client."""
    # Override the database initialization during startup
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def test_lifespan(app):
        # Skip database initialization for tests
        yield

    app.router.lifespan_context = test_lifespan

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.router.lifespan_context = original_lifespan


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator:
    """Create a test client with async database session."""

    async def override_get_db():
        yield db_session

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    # Override the database initialization during startup
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def test_lifespan(app):
        # Skip database initialization for tests
        yield

    app.router.lifespan_context = test_lifespan

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.router.lifespan_context = original_lifespan


@pytest.fixture
def test_user():
    """Create a test user for authentication."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with a test token."""
    token = create_access_token(data={"sub": test_user["email"]})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(async_client, test_user, db_session):
    """Create a test client with an authenticated user."""
    # First, create the user in the database
    from app.auth.password import get_password_hash
    from app.models.user import User

    hashed_password = get_password_hash(test_user["password"])
    db_user = User(
        email=test_user["email"],
        username=test_user["username"],
        hashed_password=hashed_password,
        first_name=test_user["first_name"],
        last_name=test_user["last_name"],
        is_active=True,
        is_verified=True,
    )

    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)

    # Create auth headers
    token = create_access_token(data={"sub": test_user["email"]})
    async_client.headers.update({"Authorization": f"Bearer {token}"})

    return async_client, db_user


@pytest.fixture
def sample_account_data():
    """Sample account data for testing."""
    return {
        "name": "Test Checking Account",
        "type": "checking",
        "institution_name": "Test Bank",
        "current_balance": 5000.00,
        "available_balance": 4800.00,
        "currency": "USD",
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "account_id": 1,
        "amount": -50.00,
        "currency": "USD",
        "date": "2024-01-15",
        "description": "Grocery Store Purchase",
        "merchant_name": "Whole Foods",
        "category": "food_and_drink",
        "subcategory": "groceries",
        "is_pending": False,
        "is_recurring": False,
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "name": "Test Portfolio",
        "description": "A test investment portfolio",
        "currency": "USD",
        "is_default": True,
    }
