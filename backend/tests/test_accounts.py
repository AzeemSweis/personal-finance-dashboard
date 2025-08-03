import pytest
from fastapi import status


class TestAccountsEndpoints:
    """Test accounts endpoints."""

    @pytest.mark.asyncio
    async def test_get_accounts_empty(self, authenticated_client):
        """Test getting accounts when user has no accounts."""
        client, user = authenticated_client

        response = client.get("/accounts")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_create_account_success(self, authenticated_client, sample_account_data):
        """Test successful account creation."""
        client, user = authenticated_client

        response = client.post("/accounts", json=sample_account_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == sample_account_data["name"]
        assert data["type"] == sample_account_data["type"]
        assert data["institution_name"] == sample_account_data["institution_name"]
        assert data["current_balance"] == sample_account_data["current_balance"]
        assert data["available_balance"] == sample_account_data["available_balance"]
        assert data["currency"] == sample_account_data["currency"]
        assert data["user_id"] == user.id
        assert data["is_active"] is True
        assert data["is_archived"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_account_missing_required_fields(self, authenticated_client):
        """Test account creation with missing required fields."""
        client, user = authenticated_client

        incomplete_data = {
            "name": "Test Account"
            # Missing type and current_balance
        }

        response = client.post("/accounts", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_account_invalid_type(
        self, authenticated_client, sample_account_data
    ):
        """Test account creation with invalid account type."""
        client, user = authenticated_client

        invalid_data = sample_account_data.copy()
        invalid_data["type"] = "invalid_type"

        response = client.post("/accounts", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_get_accounts_with_data(
        self, authenticated_client, sample_account_data, db_session
    ):
        """Test getting accounts when user has accounts."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Get all accounts
        response = client.get("/accounts")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        account = data[0]
        assert account["name"] == sample_account_data["name"]
        assert account["type"] == sample_account_data["type"]
        assert account["user_id"] == user.id

    @pytest.mark.asyncio
    async def test_get_account_by_id_success(self, authenticated_client, sample_account_data):
        """Test getting a specific account by ID."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Get the account
        response = client.get(f"/accounts/{account_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == sample_account_data["name"]

    @pytest.mark.asyncio
    async def test_get_account_by_id_not_found(self, authenticated_client):
        """Test getting a non-existent account."""
        client, user = authenticated_client

        response = client.get("/accounts/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Account not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_account_by_id_unauthorized(self, client, sample_account_data):
        """Test getting an account without authentication."""
        response = client.get("/accounts/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_account_by_id_wrong_user(
        self, authenticated_client, sample_account_data, db_session
    ):
        """Test getting an account that belongs to another user."""
        client, user = authenticated_client

        # Create an account for the current user
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Create another user and try to access the account
        from app.auth.password import get_password_hash
        from app.models.user import User

        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True,
        )

        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Try to access the account with the other user's token
        from app.auth import create_access_token

        other_token = create_access_token(data={"sub": other_user.email})
        client.headers.update({"Authorization": f"Bearer {other_token}"})

        response = client.get(f"/accounts/{account_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_account_success(self, authenticated_client, sample_account_data):
        """Test successful account update."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Update the account
        update_data = {"name": "Updated Account Name", "current_balance": 7500.00}

        response = client.put(f"/accounts/{account_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["current_balance"] == update_data["current_balance"]
        # Other fields should remain unchanged
        assert data["type"] == sample_account_data["type"]
        assert data["institution_name"] == sample_account_data["institution_name"]

    @pytest.mark.asyncio
    async def test_update_account_not_found(self, authenticated_client):
        """Test updating a non-existent account."""
        client, user = authenticated_client

        update_data = {"name": "Updated Name"}
        response = client.put("/accounts/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_account_invalid_data(
        self, authenticated_client, sample_account_data
    ):
        """Test updating account with invalid data."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Try to update with invalid type
        update_data = {"type": "invalid_type"}
        response = client.put(f"/accounts/{account_id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_delete_account_success(self, authenticated_client, sample_account_data):
        """Test successful account deletion (soft delete)."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Delete the account
        response = client.delete(f"/accounts/{account_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the account is soft deleted (archived)
        get_response = client.get(f"/accounts/{account_id}")
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["is_archived"] is True

    @pytest.mark.asyncio
    async def test_delete_account_not_found(self, authenticated_client):
        """Test deleting a non-existent account."""
        client, user = authenticated_client

        response = client.delete("/accounts/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_accounts_excludes_archived(
        self, authenticated_client, sample_account_data
    ):
        """Test that archived accounts are excluded from the list."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Archive the account
        client.delete(f"/accounts/{account_id}")

        # Get accounts list
        response = client.get("/accounts")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 0  # Archived account should not appear in list
