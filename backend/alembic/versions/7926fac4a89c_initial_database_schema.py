"""Initial database schema

Revision ID: 7926fac4a89c
Revises: 
Create Date: 2025-08-01 23:19:17.305339

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7926fac4a89c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    account_type = postgresql.ENUM('checking', 'savings', 'credit_card', 'investment', 'retirement', 'loan', 'mortgage', 'other', name='accounttype')
    account_type.create(op.get_bind())
    
    transaction_category = postgresql.ENUM('food_and_drink', 'shopping', 'transportation', 'travel', 'entertainment', 'health_and_fitness', 'home_improvement', 'personal_care', 'education', 'business_services', 'government_services', 'transfer', 'payment', 'income', 'investment', 'other', name='transactioncategory')
    transaction_category.create(op.get_bind())
    
    investment_type = postgresql.ENUM('stock', 'bond', 'etf', 'mutual_fund', 'option', 'future', 'crypto', 'commodity', 'real_estate', 'other', name='investmenttype')
    investment_type.create(op.get_bind())
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('preferences', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create accounts table
    op.create_table('accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plaid_account_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('checking', 'savings', 'credit_card', 'investment', 'retirement', 'loan', 'mortgage', 'other', name='accounttype'), nullable=False),
        sa.Column('institution_name', sa.String(length=255), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('current_balance', sa.Float(), nullable=False),
        sa.Column('available_balance', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_plaid_account_id'), 'accounts', ['plaid_account_id'], unique=True)
    
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('plaid_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('merchant_name', sa.String(length=255), nullable=True),
        sa.Column('category', sa.Enum('food_and_drink', 'shopping', 'transportation', 'travel', 'entertainment', 'health_and_fitness', 'home_improvement', 'personal_care', 'education', 'business_services', 'government_services', 'transfer', 'payment', 'income', 'investment', 'other', name='transactioncategory'), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('is_pending', sa.Boolean(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('check_number', sa.String(length=50), nullable=True),
        sa.Column('payment_channel', sa.String(length=50), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_plaid_transaction_id'), 'transactions', ['plaid_transaction_id'], unique=True)
    op.create_index(op.f('ix_transactions_date'), 'transactions', ['date'], unique=False)
    
    # Create investments table
    op.create_table('investments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('stock', 'bond', 'etf', 'mutual_fund', 'option', 'future', 'crypto', 'commodity', 'real_estate', 'other', name='investmenttype'), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('price_date', sa.Date(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('pe_ratio', sa.Float(), nullable=True),
        sa.Column('dividend_yield', sa.Float(), nullable=True),
        sa.Column('expense_ratio', sa.Float(), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investments_id'), 'investments', ['id'], unique=False)
    op.create_index(op.f('ix_investments_symbol'), 'investments', ['symbol'], unique=False)
    
    # Create portfolios table
    op.create_table('portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('target_allocation', sa.Text(), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolios_id'), 'portfolios', ['id'], unique=False)
    
    # Create portfolio_items table
    op.create_table('portfolio_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('investment_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('average_cost', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('unrealized_gain_loss', sa.Float(), nullable=False),
        sa.Column('unrealized_gain_loss_percent', sa.Float(), nullable=False),
        sa.Column('target_allocation', sa.Float(), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['investment_id'], ['investments.id'], ),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_items_id'), 'portfolio_items', ['id'], unique=False)
    
    # Create balance_snapshots table
    op.create_table('balance_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('available_balance', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_balance_snapshots_id'), 'balance_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_balance_snapshots_date'), 'balance_snapshots', ['date'], unique=False)
    
    # Create plaid_connections table
    op.create_table('plaid_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plaid_item_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('institution_id', sa.String(length=255), nullable=False),
        sa.Column('institution_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plaid_connections_id'), 'plaid_connections', ['id'], unique=False)
    op.create_index(op.f('ix_plaid_connections_plaid_item_id'), 'plaid_connections', ['plaid_item_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_plaid_connections_plaid_item_id'), table_name='plaid_connections')
    op.drop_index(op.f('ix_plaid_connections_id'), table_name='plaid_connections')
    op.drop_table('plaid_connections')
    
    op.drop_index(op.f('ix_balance_snapshots_date'), table_name='balance_snapshots')
    op.drop_index(op.f('ix_balance_snapshots_id'), table_name='balance_snapshots')
    op.drop_table('balance_snapshots')
    
    op.drop_index(op.f('ix_portfolio_items_id'), table_name='portfolio_items')
    op.drop_table('portfolio_items')
    
    op.drop_index(op.f('ix_portfolios_id'), table_name='portfolios')
    op.drop_table('portfolios')
    
    op.drop_index(op.f('ix_investments_symbol'), table_name='investments')
    op.drop_index(op.f('ix_investments_id'), table_name='investments')
    op.drop_table('investments')
    
    op.drop_index(op.f('ix_transactions_date'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_plaid_transaction_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    
    op.drop_index(op.f('ix_accounts_plaid_account_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE investmenttype')
    op.execute('DROP TYPE transactioncategory')
    op.execute('DROP TYPE accounttype') 