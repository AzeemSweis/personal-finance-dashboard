import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
  Home, 
  CreditCard, 
  TrendingUp, 
  BarChart3, 
  Wallet, 
  PieChart,
  Settings,
  Plus
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const router = useRouter();

  const navigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: Home,
      current: router.pathname === '/',
    },
    {
      name: 'Accounts',
      href: '/accounts',
      icon: CreditCard,
      current: router.pathname === '/accounts',
    },
    {
      name: 'Transactions',
      href: '/transactions',
      icon: TrendingUp,
      current: router.pathname === '/transactions',
    },
    {
      name: 'Portfolios',
      href: '/portfolios',
      icon: PieChart,
      current: router.pathname === '/portfolios',
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      current: router.pathname === '/analytics',
    },
    {
      name: 'Budgets',
      href: '/budgets',
      icon: Wallet,
      current: router.pathname === '/budgets',
    },
  ];

  const isActive = (href: string) => {
    if (href === '/') {
      return router.pathname === '/';
    }
    return router.pathname.startsWith(href);
  };

  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">$</span>
          </div>
          <span className="text-xl font-bold text-gray-900">Finance</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                active
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className="h-5 w-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Quick Actions */}
      <div className="p-4 border-t border-gray-200">
        <div className="space-y-2">
          <button className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors">
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </button>
          <button className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-600 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <Plus className="h-4 w-4 mr-2" />
            Add Transaction
          </button>
        </div>
      </div>

      {/* Settings Link */}
      <div className="p-4 border-t border-gray-200">
        <Link
          href="/settings"
          className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
            router.pathname === '/settings'
              ? 'bg-gray-50 text-gray-900'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          <Settings className="h-5 w-5 mr-3" />
          Settings
        </Link>
      </div>
    </div>
  );
};

export default Sidebar; 