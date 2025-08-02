import pytest
from fastapi import status
from sqlalchemy import select
from app.models.user import User


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_success(self, client, test_user):
        """Test successful user registration."""
        response = client.post("/auth/register", json=test_user)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]
        assert data["first_name"] == test_user["first_name"]
        assert data["last_name"] == test_user["last_name"]
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user, db_session):
        """Test registration with duplicate email."""
        # First registration
        response1 = client.post("/auth/register", json=test_user)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second registration with same email
        response2 = client.post("/auth/register", json=test_user)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response2.json()["detail"]

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        # First registration
        response1 = client.post("/auth/register", json=test_user)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second registration with same username but different email
        duplicate_user = test_user.copy()
        duplicate_user["email"] = "different@example.com"
        response2 = client.post("/auth/register", json=duplicate_user)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response2.json()["detail"]

    def test_register_invalid_email(self, client, test_user):
        """Test registration with invalid email."""
        invalid_user = test_user.copy()
        invalid_user["email"] = "invalid-email"
        
        response = client.post("/auth/register", json=invalid_user)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_user = {
            "email": "test@example.com",
            "username": "testuser"
            # Missing password
        }
        
        response = client.post("/auth/register", json=incomplete_user)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, test_user, db_session):
        """Test successful login."""
        # First register the user
        register_response = client.post("/auth/register", json=test_user)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Then login
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert len(data["access_token"]) > 0

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/auth/register", json=test_user)
        
        # Try to login with wrong password
        login_data = {
            "username": test_user["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_user, db_session):
        """Test login with inactive user."""
        # Register user
        register_response = client.post("/auth/register", json=test_user)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Deactivate user
        user_id = register_response.json()["id"]
        async def deactivate_user():
            result = await db_session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one()
            user.is_active = False
            await db_session.commit()
        
        import asyncio
        asyncio.run(deactivate_user())
        
        # Try to login
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in response.json()["detail"]

    def test_get_current_user_success(self, authenticated_client):
        """Test getting current user information."""
        client, user = authenticated_client
        
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert data["is_active"] == user.is_active
        assert data["is_verified"] == user.is_verified

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        client.headers.update({"Authorization": "Bearer invalid-token"})
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token."""
        from app.auth import create_access_token
        from datetime import timedelta
        
        # Create expired token
        expired_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=-30)
        )
        
        client.headers.update({"Authorization": f"Bearer {expired_token}"})
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 