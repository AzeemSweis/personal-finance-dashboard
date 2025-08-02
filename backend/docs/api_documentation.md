# API Documentation

## Overview

The Personal Finance Dashboard API provides a comprehensive set of endpoints for managing personal finances, including user authentication, account management, transaction tracking, portfolio management, and balance overview.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication via Bearer token in the Authorization header.

### Getting Started

1. **Register a new user**: `POST /auth/register`
2. **Login**: `POST /auth/login`
3. **Use the returned access token** in subsequent requests

## API Endpoints

### Authentication (`/auth`)

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### User Management (`/users`)

#### Get Current User Profile
```http
GET /users/me
Authorization: Bearer <access_token>
```

#### Update Current User Profile
```http
PUT /users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Account Management (`/accounts`)

#### Get All Accounts
```http
GET /accounts
Authorization: Bearer <access_token>
```

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Chase Checking",
    "type": "checking",
    "institution_name": "Chase Bank",
    "current_balance": 2500.00,
    "available_balance": 2500.00,
    "currency": "USD",
    "is_active": true,
    "is_archived": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Account by ID
```http
GET /accounts/{account_id}
Authorization: Bearer <access_token>
```

#### Create Account
```http
POST /accounts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Savings Account",
  "type": "savings",
  "institution_name": "Bank of America",
  "current_balance": 10000.00,
  "currency": "USD"
}
```

#### Update Account
```http
PUT /accounts/{account_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_balance": 10500.00
}
```

#### Delete Account (Soft Delete)
```http
DELETE /accounts/{account_id}
Authorization: Bearer <access_token>
```

### Transaction Management (`/transactions`)

#### Get Transactions
```http
GET /transactions?account_id=1&start_date=2024-01-01&end_date=2024-01-31&category=food_and_drink&limit=50&offset=0
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `account_id` (optional): Filter by account ID
- `start_date` (optional): Filter by start date (YYYY-MM-DD)
- `end_date` (optional): Filter by end date (YYYY-MM-DD)
- `category` (optional): Filter by transaction category
- `limit` (default: 100, max: 1000): Number of transactions to return
- `offset` (default: 0): Number of transactions to skip

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "account_id": 1,
    "amount": -45.67,
    "currency": "USD",
    "date": "2024-01-15",
    "description": "Grocery Store Purchase",
    "merchant_name": "Whole Foods",
    "category": "food_and_drink",
    "subcategory": "groceries",
    "is_pending": false,
    "is_recurring": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Get Transaction by ID
```http
GET /transactions/{transaction_id}
Authorization: Bearer <access_token>
```

#### Create Transaction
```http
POST /transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "account_id": 1,
  "amount": -25.00,
  "date": "2024-01-15",
  "description": "Coffee Shop",
  "merchant_name": "Starbucks",
  "category": "food_and_drink",
  "subcategory": "coffee"
}
```

#### Update Transaction
```http
PUT /transactions/{transaction_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": -30.00,
  "description": "Coffee Shop - Large Latte"
}
```

#### Delete Transaction
```http
DELETE /transactions/{transaction_id}
Authorization: Bearer <access_token>
```

### Balance Overview (`/balances`)

#### Get Balance Overview
```http
GET /balances/overview
Authorization: Bearer <access_token>
```

**Response**: `200 OK`
```json
{
  "total_balance": 12500.00,
  "total_available_balance": 12500.00,
  "currency": "USD",
  "accounts": [
    {
      "account_id": 1,
      "account_name": "Chase Checking",
      "account_type": "checking",
      "institution_name": "Chase Bank",
      "current_balance": 2500.00,
      "available_balance": 2500.00,
      "currency": "USD",
      "last_updated": "2024-01-01T00:00:00Z"
    }
  ],
  "net_worth_trend": [
    {
      "date": "2024-01-01",
      "balance": 12000.00
    },
    {
      "date": "2024-01-02",
      "balance": 12100.00
    }
  ],
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### Get Balance Snapshots
```http
GET /balances/snapshots?account_id=1&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

#### Get Account Balance Snapshots
```http
GET /balances/snapshots/{account_id}
Authorization: Bearer <access_token>
```

### Portfolio Management (`/portfolios`)

#### Get All Portfolios
```http
GET /portfolios
Authorization: Bearer <access_token>
```

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Main Portfolio",
    "description": "My primary investment portfolio",
    "total_value": 50000.00,
    "currency": "USD",
    "is_active": true,
    "is_default": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Portfolio by ID
```http
GET /portfolios/{portfolio_id}
Authorization: Bearer <access_token>
```

#### Create Portfolio
```http
POST /portfolios
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Retirement Portfolio",
  "description": "Long-term retirement investments",
  "currency": "USD",
  "is_default": false
}
```

#### Update Portfolio
```http
PUT /portfolios/{portfolio_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "total_value": 52000.00,
  "is_default": true
}
```

#### Delete Portfolio (Soft Delete)
```http
DELETE /portfolios/{portfolio_id}
Authorization: Bearer <access_token>
```

### Portfolio Items (`/portfolios/{portfolio_id}/items`)

#### Get Portfolio Items
```http
GET /portfolios/{portfolio_id}/items
Authorization: Bearer <access_token>
```

#### Add Portfolio Item
```http
POST /portfolios/{portfolio_id}/items
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "investment_id": 1,
  "quantity": 100,
  "average_cost": 150.00,
  "current_value": 15500.00,
  "unrealized_gain_loss": 500.00,
  "unrealized_gain_loss_percent": 3.33,
  "target_allocation": 30.0
}
```

#### Update Portfolio Item
```http
PUT /portfolios/{portfolio_id}/items/{item_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 110,
  "current_value": 17050.00,
  "unrealized_gain_loss": 2050.00,
  "unrealized_gain_loss_percent": 13.67
}
```

#### Remove Portfolio Item
```http
DELETE /portfolios/{portfolio_id}/items/{item_id}
Authorization: Bearer <access_token>
```

## Data Models

### Account Types
- `checking`: Regular checking accounts
- `savings`: Savings accounts
- `credit_card`: Credit card accounts
- `investment`: Investment accounts
- `retirement`: Retirement accounts (401k, IRA, etc.)
- `loan`: Loan accounts
- `mortgage`: Mortgage accounts
- `other`: Other account types

### Transaction Categories
- `food_and_drink`: Food and beverage purchases
- `shopping`: Retail purchases
- `transportation`: Transportation expenses
- `travel`: Travel expenses
- `entertainment`: Entertainment expenses
- `health_and_fitness`: Health and fitness expenses
- `home_improvement`: Home improvement expenses
- `personal_care`: Personal care expenses
- `education`: Education expenses
- `business_services`: Business service expenses
- `government_services`: Government service expenses
- `transfer`: Account transfers
- `payment`: Bill payments
- `income`: Income transactions
- `investment`: Investment transactions
- `other`: Other transactions

### Investment Types
- `stock`: Individual stocks
- `bond`: Bonds
- `etf`: Exchange-traded funds
- `mutual_fund`: Mutual funds
- `option`: Options
- `future`: Futures
- `crypto`: Cryptocurrencies
- `commodity`: Commodities
- `real_estate`: Real estate investments
- `other`: Other investment types

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

### Example Error Response
```json
{
  "detail": "Account not found"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in future versions.

## Pagination

For endpoints that return lists, pagination is supported via `limit` and `offset` query parameters.

## CORS

The API supports CORS for frontend integration. Allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## API Versioning

The current API version is `1.0.0`. Future versions will be available at `/v2/`, `/v3/`, etc.

## Testing

You can test the API using:
1. **Swagger UI**: Visit `http://localhost:8000/docs`
2. **ReDoc**: Visit `http://localhost:8000/redoc`
3. **cURL**: Use the examples above with cURL
4. **Postman**: Import the OpenAPI specification

## Development

### Running the API
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### Running Tests
```bash
cd backend
source venv/bin/activate
pytest
``` 