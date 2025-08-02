from datetime import date, timedelta

import pytest
from fastapi import status


class TestBalancesEndpoints:
    """Test balance overview endpoints."""

    def test_get_balance_overview_empty(self, authenticated_client):
        """Test getting balance overview when user has no accounts."""
        client, user = authenticated_client

        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total_balance"] == 0.0
        assert data["total_available_balance"] == 0.0
        assert data["currency"] == "USD"
        assert isinstance(data["accounts"], list)
        assert len(data["accounts"]) == 0
        assert isinstance(data["net_worth_trend"], list)
        assert len(data["net_worth_trend"]) == 0
        assert "last_updated" in data

    def test_get_balance_overview_with_accounts(
        self, authenticated_client, sample_account_data
    ):
        """Test getting balance overview when user has accounts."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Get balance overview
        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total_balance"] == sample_account_data["current_balance"]
        assert (
            data["total_available_balance"] == sample_account_data["available_balance"]
        )
        assert data["currency"] == "USD"
        assert len(data["accounts"]) == 1

        account = data["accounts"][0]
        assert account["account_id"] == create_response.json()["id"]
        assert account["account_name"] == sample_account_data["name"]
        assert account["account_type"] == sample_account_data["type"]
        assert account["current_balance"] == sample_account_data["current_balance"]
        assert account["available_balance"] == sample_account_data["available_balance"]
        assert account["currency"] == sample_account_data["currency"]

    def test_get_balance_overview_multiple_accounts(
        self, authenticated_client, sample_account_data
    ):
        """Test getting balance overview with multiple accounts."""
        client, user = authenticated_client

        # Create first account
        account1_data = sample_account_data.copy()
        account1_data["name"] = "Checking Account"
        account1_data["current_balance"] = 5000.00
        account1_data["available_balance"] = 4800.00

        create_response1 = client.post("/accounts", json=account1_data)
        assert create_response1.status_code == status.HTTP_201_CREATED

        # Create second account
        account2_data = sample_account_data.copy()
        account2_data["name"] = "Savings Account"
        account2_data["type"] = "savings"
        account2_data["current_balance"] = 10000.00
        account2_data["available_balance"] = 10000.00

        create_response2 = client.post("/accounts", json=account2_data)
        assert create_response2.status_code == status.HTTP_201_CREATED

        # Get balance overview
        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        expected_total = (
            account1_data["current_balance"] + account2_data["current_balance"]
        )
        expected_available = (
            account1_data["available_balance"] + account2_data["available_balance"]
        )

        assert data["total_balance"] == expected_total
        assert data["total_available_balance"] == expected_available
        assert len(data["accounts"]) == 2

    def test_get_balance_overview_excludes_archived_accounts(
        self, authenticated_client, sample_account_data
    ):
        """Test that archived accounts are excluded from balance overview."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Archive the account
        client.delete(f"/accounts/{account_id}")

        # Get balance overview
        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["total_balance"] == 0.0
        assert data["total_available_balance"] == 0.0
        assert len(data["accounts"]) == 0

    def test_get_balance_overview_unauthorized(self, client):
        """Test getting balance overview without authentication."""
        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_balance_snapshots_empty(self, authenticated_client):
        """Test getting balance snapshots when user has no snapshots."""
        client, user = authenticated_client

        response = client.get("/balances/snapshots")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_balance_snapshots_with_filters(self, authenticated_client):
        """Test getting balance snapshots with query parameters."""
        client, user = authenticated_client

        # Test with account_id filter
        response = client.get("/balances/snapshots?account_id=1")
        assert response.status_code == status.HTTP_200_OK

        # Test with date filters
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()
        end_date = today.isoformat()

        response = client.get(
            f"/balances/snapshots?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_account_balance_snapshots_empty(
        self, authenticated_client, sample_account_data
    ):
        """Test getting account-specific balance snapshots when none exist."""
        client, user = authenticated_client

        # Create an account
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Get snapshots for the account
        response = client.get(f"/balances/snapshots/{account_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No balance snapshots found" in response.json()["detail"]

    def test_get_account_balance_snapshots_wrong_account(self, authenticated_client):
        """Test getting balance snapshots for non-existent account."""
        client, user = authenticated_client

        response = client.get("/balances/snapshots/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_account_balance_snapshots_unauthorized(self, client):
        """Test getting account balance snapshots without authentication."""
        response = client.get("/balances/snapshots/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_account_balance_snapshots_wrong_user(
        self, authenticated_client, sample_account_data, db_session
    ):
        """Test getting balance snapshots for account belonging to another user."""
        client, user = authenticated_client

        # Create an account for the current user
        create_response = client.post("/accounts", json=sample_account_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]

        # Create another user and try to access the account snapshots
        from app.auth.password import get_password_hash
        from app.models.user import User

        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True,
        )

        async def create_other_user():
            db_session.add(other_user)
            await db_session.commit()
            await db_session.refresh(other_user)

        import asyncio

        asyncio.run(create_other_user())

        # Try to access the account snapshots with the other user's token
        from app.auth import create_access_token

        other_token = create_access_token(data={"sub": other_user.email})
        client.headers.update({"Authorization": f"Bearer {other_token}"})

        response = client.get(f"/balances/snapshots/{account_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_balance_overview_currency_handling(
        self, authenticated_client, sample_account_data
    ):
        """Test balance overview with different currencies."""
        client, user = authenticated_client

        # Create account with USD
        usd_account = sample_account_data.copy()
        usd_account["currency"] = "USD"
        usd_account["current_balance"] = 1000.00

        create_response1 = client.post("/accounts", json=usd_account)
        assert create_response1.status_code == status.HTTP_201_CREATED

        # Create account with EUR
        eur_account = sample_account_data.copy()
        eur_account["name"] = "EUR Account"
        eur_account["currency"] = "EUR"
        eur_account["current_balance"] = 800.00

        create_response2 = client.post("/accounts", json=eur_account)
        assert create_response2.status_code == status.HTTP_201_CREATED

        # Get balance overview
        response = client.get("/balances/overview")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should show USD as default currency
        assert data["currency"] == "USD"
        # Should include both accounts
        assert len(data["accounts"]) == 2

        # Verify individual account currencies
        usd_account_data = next(
            acc for acc in data["accounts"] if acc["currency"] == "USD"
        )
        eur_account_data = next(
            acc for acc in data["accounts"] if acc["currency"] == "EUR"
        )

        assert usd_account_data["current_balance"] == 1000.00
        assert eur_account_data["current_balance"] == 800.00
