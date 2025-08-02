import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../stores/authStore';
import { balancesApi, transactionsApi, formatCurrency } from '../services/api';
import { BalanceOverview, Transaction } from '../services/api';
import Layout from '../components/Layout/Layout';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Plus
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [balanceOverview, setBalanceOverview] = useState<BalanceOverview | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [balanceData, transactionsData] = await Promise.all([
          balancesApi.getBalanceOverview(),
          transactionsApi.getTransactions({ limit: 5 })
        ]);
        
        setBalanceOverview(balanceData);
        setRecentTransactions(transactionsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow-soft">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-soft">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const getAccountTypeColor = (type: string) => {
    const colors = {
      checking: 'bg-blue-100 text-blue-800',
      savings: 'bg-green-100 text-green-800',
      credit_card: 'bg-purple-100 text-purple-800',
      investment: 'bg-yellow-100 text-yellow-800',
      retirement: 'bg-orange-100 text-orange-800',
      loan: 'bg-red-100 text-red-800',
      mortgage: 'bg-indigo-100 text-indigo-800',
      other: 'bg-gray-100 text-gray-800',
    };
    return colors[type as keyof typeof colors] || colors.other;
  };

  const getTransactionIcon = (amount: number) => {
    return amount > 0 ? (
      <ArrowUpRight className="h-4 w-4 text-success-500" />
    ) : (
      <ArrowDownRight className="h-4 w-4 text-danger-500" />
    );
  };

  return (
    <Layout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back! Here's an overview of your financial status.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Balance */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                {balanceOverview ? formatCurrency(balanceOverview.total_balance) : '$0.00'}
              </p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <DollarSign className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-success-500 mr-1" />
            <span className="text-success-600">+2.5%</span>
            <span className="text-gray-500 ml-1">from last month</span>
          </div>
        </div>

        {/* Available Balance */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Available Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                {balanceOverview ? formatCurrency(balanceOverview.total_available_balance) : '$0.00'}
              </p>
            </div>
            <div className="p-3 bg-success-100 rounded-lg">
              <CreditCard className="h-6 w-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-success-500 mr-1" />
            <span className="text-success-600">+1.8%</span>
            <span className="text-gray-500 ml-1">from last month</span>
          </div>
        </div>

        {/* Monthly Income */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Income</p>
              <p className="text-2xl font-bold text-gray-900">$8,500</p>
            </div>
            <div className="p-3 bg-success-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-success-500 mr-1" />
            <span className="text-success-600">+5.2%</span>
            <span className="text-gray-500 ml-1">from last month</span>
          </div>
        </div>

        {/* Monthly Expenses */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Expenses</p>
              <p className="text-2xl font-bold text-gray-900">$3,200</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <TrendingDown className="h-6 w-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingDown className="h-4 w-4 text-danger-500 mr-1" />
            <span className="text-danger-600">-2.1%</span>
            <span className="text-gray-500 ml-1">from last month</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Net Worth Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Net Worth Trend</h3>
            <button className="text-sm text-primary-600 hover:text-primary-500">
              <Eye className="h-4 w-4" />
            </button>
          </div>
          
          {balanceOverview && balanceOverview.net_worth_trend.length > 0 ? (
            <div className="h-64 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-8 w-8 text-primary-600" />
                </div>
                <p className="text-sm text-gray-600">Chart will be implemented with Recharts</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-sm text-gray-500">No data available</p>
                <p className="text-xs text-gray-400 mt-1">Add accounts to see your net worth trend</p>
              </div>
            </div>
          )}
        </div>

        {/* Recent Transactions */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
            <button 
              onClick={() => router.push('/transactions')}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              View all
            </button>
          </div>
          
          {recentTransactions.length > 0 ? (
            <div className="space-y-4">
              {recentTransactions.map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      {getTransactionIcon(transaction.amount)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{transaction.description}</p>
                      <p className="text-xs text-gray-500">
                        {transaction.merchant_name && `${transaction.merchant_name} • `}
                        {new Date(transaction.date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${
                      transaction.amount > 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {transaction.amount > 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                    </p>
                    {transaction.category && (
                      <span className={`text-xs px-2 py-1 rounded-full ${getAccountTypeColor(transaction.category)}`}>
                        {transaction.category.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CreditCard className="h-6 w-6 text-gray-400" />
              </div>
              <p className="text-sm text-gray-500">No recent transactions</p>
              <button className="mt-2 text-sm text-primary-600 hover:text-primary-500 flex items-center mx-auto">
                <Plus className="h-4 w-4 mr-1" />
                Add transaction
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Account Overview */}
      {balanceOverview && balanceOverview.accounts.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Account Overview</h3>
            <button 
              onClick={() => router.push('/accounts')}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              View all accounts
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {balanceOverview.accounts.slice(0, 6).map((account) => (
              <div key={account.account_id} className="card p-4 hover:shadow-medium transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{account.account_name}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${getAccountTypeColor(account.account_type)}`}>
                    {account.account_type.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(account.current_balance, account.currency)}
                </p>
                {account.institution_name && (
                  <p className="text-xs text-gray-500 mt-1">{account.institution_name}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
};

export default DashboardPage; 