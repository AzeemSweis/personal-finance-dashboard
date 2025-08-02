import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

// Account types
export interface Account {
  id: number;
  user_id: number;
  name: string;
  type: string;
  institution_name?: string;
  current_balance: number;
  available_balance?: number;
  currency: string;
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  type: string;
  institution_name?: string;
  current_balance: number;
  available_balance?: number;
  currency?: string;
}

export interface AccountUpdate {
  name?: string;
  type?: string;
  institution_name?: string;
  current_balance?: number;
  available_balance?: number;
  is_active?: boolean;
}

// Transaction types
export interface Transaction {
  id: number;
  account_id: number;
  amount: number;
  currency: string;
  date: string;
  description: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  is_pending: boolean;
  is_recurring: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: number;
  amount: number;
  currency?: string;
  date: string;
  description: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  is_pending?: boolean;
  is_recurring?: boolean;
}

export interface TransactionUpdate {
  amount?: number;
  currency?: string;
  date?: string;
  description?: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  is_pending?: boolean;
  is_recurring?: boolean;
}

// Balance types
export interface BalanceOverview {
  total_balance: number;
  total_available_balance: number;
  currency: string;
  accounts: AccountBalance[];
  net_worth_trend: NetWorthPoint[];
  last_updated: string;
}

export interface AccountBalance {
  account_id: number;
  account_name: string;
  account_type: string;
  institution_name?: string;
  current_balance: number;
  available_balance?: number;
  currency: string;
  last_updated: string;
}

export interface NetWorthPoint {
  date: string;
  balance: number;
}

// Portfolio types
export interface Portfolio {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  total_value: number;
  currency: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface PortfolioCreate {
  name: string;
  description?: string;
  currency?: string;
  is_default?: boolean;
}

export interface PortfolioUpdate {
  name?: string;
  description?: string;
  total_value?: number;
  currency?: string;
  is_active?: boolean;
  is_default?: boolean;
}

// API service functions
export const authApi = {
  // Register new user
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<ApiResponse<User>>('/auth/register', data);
    return response.data.data;
  },

  // Login user
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<ApiResponse<User>>('/auth/me');
    return response.data.data;
  },
};

export const userApi = {
  // Get current user profile
  getProfile: async (): Promise<User> => {
    const response = await api.get<ApiResponse<User>>('/users/me');
    return response.data.data;
  },

  // Update user profile
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<ApiResponse<User>>('/users/me', data);
    return response.data.data;
  },
};

export const accountsApi = {
  // Get all accounts
  getAccounts: async (): Promise<Account[]> => {
    const response = await api.get<ApiResponse<Account[]>>('/accounts');
    return response.data.data;
  },

  // Get account by ID
  getAccount: async (id: number): Promise<Account> => {
    const response = await api.get<ApiResponse<Account>>(`/accounts/${id}`);
    return response.data.data;
  },

  // Create account
  createAccount: async (data: AccountCreate): Promise<Account> => {
    const response = await api.post<ApiResponse<Account>>('/accounts', data);
    return response.data.data;
  },

  // Update account
  updateAccount: async (id: number, data: AccountUpdate): Promise<Account> => {
    const response = await api.put<ApiResponse<Account>>(`/accounts/${id}`, data);
    return response.data.data;
  },

  // Delete account
  deleteAccount: async (id: number): Promise<void> => {
    await api.delete(`/accounts/${id}`);
  },
};

export const transactionsApi = {
  // Get transactions with filters
  getTransactions: async (params?: {
    account_id?: number;
    start_date?: string;
    end_date?: string;
    category?: string;
    limit?: number;
    offset?: number;
  }): Promise<Transaction[]> => {
    const response = await api.get<ApiResponse<Transaction[]>>('/transactions', { params });
    return response.data.data;
  },

  // Get transaction by ID
  getTransaction: async (id: number): Promise<Transaction> => {
    const response = await api.get<ApiResponse<Transaction>>(`/transactions/${id}`);
    return response.data.data;
  },

  // Create transaction
  createTransaction: async (data: TransactionCreate): Promise<Transaction> => {
    const response = await api.post<ApiResponse<Transaction>>('/transactions', data);
    return response.data.data;
  },

  // Update transaction
  updateTransaction: async (id: number, data: TransactionUpdate): Promise<Transaction> => {
    const response = await api.put<ApiResponse<Transaction>>(`/transactions/${id}`, data);
    return response.data.data;
  },

  // Delete transaction
  deleteTransaction: async (id: number): Promise<void> => {
    await api.delete(`/transactions/${id}`);
  },
};

export const balancesApi = {
  // Get balance overview
  getBalanceOverview: async (): Promise<BalanceOverview> => {
    const response = await api.get<ApiResponse<BalanceOverview>>('/balances/overview');
    return response.data.data;
  },

  // Get balance snapshots
  getBalanceSnapshots: async (params?: {
    account_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<any[]> => {
    const response = await api.get<ApiResponse<any[]>>('/balances/snapshots', { params });
    return response.data.data;
  },
};

export const portfoliosApi = {
  // Get all portfolios
  getPortfolios: async (): Promise<Portfolio[]> => {
    const response = await api.get<ApiResponse<Portfolio[]>>('/portfolios');
    return response.data.data;
  },

  // Get portfolio by ID
  getPortfolio: async (id: number): Promise<Portfolio> => {
    const response = await api.get<ApiResponse<Portfolio>>(`/portfolios/${id}`);
    return response.data.data;
  },

  // Create portfolio
  createPortfolio: async (data: PortfolioCreate): Promise<Portfolio> => {
    const response = await api.post<ApiResponse<Portfolio>>('/portfolios', data);
    return response.data.data;
  },

  // Update portfolio
  updatePortfolio: async (id: number, data: PortfolioUpdate): Promise<Portfolio> => {
    const response = await api.put<ApiResponse<Portfolio>>(`/portfolios/${id}`, data);
    return response.data.data;
  },

  // Delete portfolio
  deletePortfolio: async (id: number): Promise<void> => {
    await api.delete(`/portfolios/${id}`);
  },
};

// Utility functions
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (date: string): string => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default api; 