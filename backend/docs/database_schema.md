# Database Schema Documentation

## Overview

The Personal Finance Dashboard uses PostgreSQL as the primary database with a comprehensive schema designed to support both balance overview and investment tracking features. The schema is optimized for financial data with proper indexing, relationships, and data integrity constraints.

## Database Models

### 1. Users Table
**Purpose**: Store user authentication and profile information

**Key Fields**:
- `id`: Primary key
- `email`: Unique email address for login
- `username`: Unique username
- `hashed_password`: Encrypted password
- `is_active`: Account status
- `is_verified`: Email verification status
- `preferences`: JSON string for user preferences

**Relationships**:
- One-to-Many with Accounts
- One-to-Many with Portfolios
- One-to-Many with PlaidConnections

### 2. Accounts Table
**Purpose**: Store financial account information from various institutions

**Key Fields**:
- `id`: Primary key
- `user_id`: Foreign key to Users
- `plaid_account_id`: Plaid's unique account identifier
- `name`: Account display name
- `type`: Account type (checking, savings, investment, etc.)
- `institution_name`: Financial institution name
- `current_balance`: Current account balance
- `available_balance`: Available balance (for credit cards)
- `currency`: Account currency (default: USD)

**Account Types**:
- `checking`: Regular checking accounts
- `savings`: Savings accounts
- `credit_card`: Credit card accounts
- `investment`: Investment accounts
- `retirement`: Retirement accounts (401k, IRA, etc.)
- `loan`: Loan accounts
- `mortgage`: Mortgage accounts
- `other`: Other account types

### 3. Transactions Table
**Purpose**: Store individual financial transactions

**Key Fields**:
- `id`: Primary key
- `account_id`: Foreign key to Accounts
- `plaid_transaction_id`: Plaid's unique transaction identifier
- `amount`: Transaction amount (positive for income, negative for expenses)
- `date`: Transaction date
- `description`: Transaction description
- `merchant_name`: Merchant name
- `category`: Transaction category
- `is_pending`: Whether transaction is pending
- `is_recurring`: Whether transaction is recurring

**Transaction Categories**:
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

### 4. Portfolios Table
**Purpose**: Store investment portfolio information

**Key Fields**:
- `id`: Primary key
- `user_id`: Foreign key to Users
- `name`: Portfolio name
- `description`: Portfolio description
- `total_value`: Total portfolio value
- `currency`: Portfolio currency
- `is_default`: Whether this is the default portfolio
- `target_allocation`: JSON string for target asset allocation

### 5. PortfolioItems Table
**Purpose**: Store individual investments within portfolios

**Key Fields**:
- `id`: Primary key
- `portfolio_id`: Foreign key to Portfolios
- `investment_id`: Foreign key to Investments
- `quantity`: Number of shares/units
- `average_cost`: Average cost per share/unit
- `current_value`: Current market value
- `unrealized_gain_loss`: Unrealized gain/loss amount
- `unrealized_gain_loss_percent`: Unrealized gain/loss percentage
- `target_allocation`: Target allocation percentage

### 6. Investments Table
**Purpose**: Store investment security information

**Key Fields**:
- `id`: Primary key
- `symbol`: Investment symbol/ticker
- `name`: Investment name
- `type`: Investment type
- `exchange`: Trading exchange
- `current_price`: Current market price
- `price_date`: Date of current price
- `market_cap`: Market capitalization
- `pe_ratio`: Price-to-earnings ratio
- `dividend_yield`: Dividend yield percentage
- `expense_ratio`: Expense ratio (for ETFs/mutual funds)
- `sector`: Investment sector
- `industry`: Investment industry
- `country`: Investment country

**Investment Types**:
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

### 7. BalanceSnapshots Table
**Purpose**: Store historical account balance data for trend analysis

**Key Fields**:
- `id`: Primary key
- `account_id`: Foreign key to Accounts
- `date`: Snapshot date
- `balance`: Account balance on that date
- `available_balance`: Available balance on that date
- `currency`: Account currency

### 8. PlaidConnections Table
**Purpose**: Store Plaid API connection information

**Key Fields**:
- `id`: Primary key
- `user_id`: Foreign key to Users
- `plaid_item_id`: Plaid's item identifier
- `access_token`: Encrypted Plaid access token
- `institution_id`: Plaid institution identifier
- `institution_name`: Institution name
- `is_active`: Connection status
- `last_sync_at`: Last synchronization timestamp
- `sync_status`: Synchronization status
- `error_message`: Error message if sync failed

## Database Relationships

### One-to-Many Relationships
- User → Accounts
- User → Portfolios
- User → PlaidConnections
- Account → Transactions
- Account → BalanceSnapshots
- Portfolio → PortfolioItems

### Many-to-One Relationships
- PortfolioItem → Investment

## Indexing Strategy

### Primary Indexes
- All primary keys are automatically indexed

### Secondary Indexes
- `users.email`: For fast user lookup by email
- `users.username`: For fast user lookup by username
- `accounts.user_id`: For fast account lookup by user
- `accounts.plaid_account_id`: For Plaid integration
- `transactions.account_id`: For fast transaction lookup by account
- `transactions.date`: For date-based queries
- `transactions.plaid_transaction_id`: For Plaid integration
- `balance_snapshots.account_id`: For account balance history
- `balance_snapshots.date`: For date-based balance queries
- `investments.symbol`: For fast investment lookup by symbol
- `portfolio_items.portfolio_id`: For fast portfolio item lookup
- `plaid_connections.user_id`: For fast connection lookup by user

## Data Integrity Constraints

### Foreign Key Constraints
- All foreign key relationships are properly constrained
- Cascade delete for user-related data
- Restrict delete for critical financial data

### Unique Constraints
- User email addresses must be unique
- User usernames must be unique
- Plaid account IDs must be unique
- Plaid transaction IDs must be unique
- Plaid item IDs must be unique

### Check Constraints
- Account balances cannot be negative (except for credit cards)
- Transaction amounts must be non-zero
- Portfolio item quantities must be positive
- Investment prices must be positive

## Data Types and Precision

### Monetary Values
- All monetary values use `FLOAT` type for precision
- Currency codes use `VARCHAR(3)` for ISO 4217 codes
- Percentages use `FLOAT` with values between 0 and 100

### Text Fields
- Account names: `VARCHAR(255)`
- Transaction descriptions: `VARCHAR(500)`
- Investment symbols: `VARCHAR(20)`
- Institution names: `VARCHAR(255)`

### Date/Time Fields
- Transaction dates: `DATE`
- Balance snapshot dates: `DATE`
- Created/updated timestamps: `TIMESTAMP WITH TIME ZONE`

## Security Considerations

### Data Encryption
- Passwords are hashed using bcrypt
- Plaid access tokens are encrypted at rest
- Sensitive account numbers are masked

### Access Control
- Row-level security through user_id foreign keys
- All queries filter by authenticated user
- No cross-user data access

### Audit Trail
- All tables include created_at and updated_at timestamps
- Balance snapshots provide historical audit trail
- Transaction history is immutable

## Performance Optimizations

### Query Optimization
- Proper indexing on frequently queried fields
- Composite indexes for common query patterns
- Partitioning strategy for large tables (future)

### Caching Strategy
- Redis caching for frequently accessed data
- Balance overview cached with TTL
- Portfolio calculations cached

### Connection Pooling
- SQLAlchemy connection pooling configured
- Pool size optimized for expected load
- Connection recycling for long-running processes

## Migration Strategy

### Alembic Migrations
- All schema changes use Alembic migrations
- Forward and backward migration support
- Data migration scripts for complex changes

### Version Control
- Migration files version controlled
- Deployment scripts include migration steps
- Rollback procedures documented

## Backup and Recovery

### Backup Strategy
- Daily automated backups
- Point-in-time recovery capability
- Cross-region backup replication

### Data Retention
- Transaction data retained indefinitely
- Balance snapshots retained for 7 years
- Audit logs retained for compliance

## Future Enhancements

### Planned Schema Extensions
- Budget planning tables
- Financial goals tracking
- Tax optimization data
- Estate planning information
- Advanced analytics tables

### Performance Improvements
- Table partitioning for large datasets
- Materialized views for complex calculations
- Read replicas for analytics queries 