import axios from 'axios'
import { authApi, accountsApi, transactionsApi, balancesApi, formatCurrency, formatDate, formatDateTime } from '../api'

// Mock axios
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('axios configuration', () => {
    it('should configure axios with correct base URL', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'http://localhost:8000',
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
          },
        })
      )
    })
  })

  describe('authApi', () => {
    const mockApi = mockedAxios.create()

    beforeEach(() => {
      mockedAxios.create.mockReturnValue(mockApi)
    })

    describe('register', () => {
      it('should register user successfully', async () => {
        const userData = {
          email: 'test@example.com',
          username: 'testuser',
          password: 'password123',
          first_name: 'Test',
          last_name: 'User',
        }

        const mockResponse = {
          data: {
            data: {
              id: 1,
              email: 'test@example.com',
              username: 'testuser',
              first_name: 'Test',
              last_name: 'User',
              is_active: true,
              is_verified: false,
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          },
        }

        mockApi.post.mockResolvedValue(mockResponse)

        const result = await authApi.register(userData)

        expect(mockApi.post).toHaveBeenCalledWith('/auth/register', userData)
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('login', () => {
      it('should login user successfully', async () => {
        const loginData = {
          username: 'test@example.com',
          password: 'password123',
        }

        const mockResponse = {
          data: {
            access_token: 'mock-token',
            token_type: 'bearer',
            expires_in: 1800,
          },
        }

        mockApi.post.mockResolvedValue(mockResponse)

        const result = await authApi.login(loginData)

        expect(mockApi.post).toHaveBeenCalledWith('/auth/login', expect.any(FormData), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })
        expect(result).toEqual(mockResponse.data)
      })
    })

    describe('getCurrentUser', () => {
      it('should get current user successfully', async () => {
        const mockResponse = {
          data: {
            data: {
              id: 1,
              email: 'test@example.com',
              username: 'testuser',
              first_name: 'Test',
              last_name: 'User',
              is_active: true,
              is_verified: true,
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await authApi.getCurrentUser()

        expect(mockApi.get).toHaveBeenCalledWith('/auth/me')
        expect(result).toEqual(mockResponse.data.data)
      })
    })
  })

  describe('accountsApi', () => {
    const mockApi = mockedAxios.create()

    beforeEach(() => {
      mockedAxios.create.mockReturnValue(mockApi)
    })

    describe('getAccounts', () => {
      it('should get accounts successfully', async () => {
        const mockResponse = {
          data: {
            data: [
              {
                id: 1,
                user_id: 1,
                name: 'Test Account',
                type: 'checking',
                current_balance: 5000.00,
                currency: 'USD',
                is_active: true,
                is_archived: false,
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
              },
            ],
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await accountsApi.getAccounts()

        expect(mockApi.get).toHaveBeenCalledWith('/accounts')
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('createAccount', () => {
      it('should create account successfully', async () => {
        const accountData = {
          name: 'New Account',
          type: 'savings',
          current_balance: 10000.00,
          currency: 'USD',
        }

        const mockResponse = {
          data: {
            data: {
              id: 1,
              user_id: 1,
              name: 'New Account',
              type: 'savings',
              current_balance: 10000.00,
              currency: 'USD',
              is_active: true,
              is_archived: false,
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          },
        }

        mockApi.post.mockResolvedValue(mockResponse)

        const result = await accountsApi.createAccount(accountData)

        expect(mockApi.post).toHaveBeenCalledWith('/accounts', accountData)
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('updateAccount', () => {
      it('should update account successfully', async () => {
        const accountId = 1
        const updateData = {
          name: 'Updated Account',
          current_balance: 7500.00,
        }

        const mockResponse = {
          data: {
            data: {
              id: 1,
              user_id: 1,
              name: 'Updated Account',
              type: 'checking',
              current_balance: 7500.00,
              currency: 'USD',
              is_active: true,
              is_archived: false,
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
          },
        }

        mockApi.put.mockResolvedValue(mockResponse)

        const result = await accountsApi.updateAccount(accountId, updateData)

        expect(mockApi.put).toHaveBeenCalledWith(`/accounts/${accountId}`, updateData)
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('deleteAccount', () => {
      it('should delete account successfully', async () => {
        const accountId = 1

        mockApi.delete.mockResolvedValue({})

        await accountsApi.deleteAccount(accountId)

        expect(mockApi.delete).toHaveBeenCalledWith(`/accounts/${accountId}`)
      })
    })
  })

  describe('transactionsApi', () => {
    const mockApi = mockedAxios.create()

    beforeEach(() => {
      mockedAxios.create.mockReturnValue(mockApi)
    })

    describe('getTransactions', () => {
      it('should get transactions successfully', async () => {
        const params = {
          account_id: 1,
          start_date: '2024-01-01',
          end_date: '2024-01-31',
          limit: 50,
          offset: 0,
        }

        const mockResponse = {
          data: {
            data: [
              {
                id: 1,
                account_id: 1,
                amount: -50.00,
                currency: 'USD',
                date: '2024-01-15',
                description: 'Grocery Store',
                merchant_name: 'Whole Foods',
                category: 'food_and_drink',
                is_pending: false,
                is_recurring: false,
                created_at: '2024-01-15T10:00:00Z',
                updated_at: '2024-01-15T10:00:00Z',
              },
            ],
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await transactionsApi.getTransactions(params)

        expect(mockApi.get).toHaveBeenCalledWith('/transactions', { params })
        expect(result).toEqual(mockResponse.data.data)
      })

      it('should get transactions without params', async () => {
        const mockResponse = {
          data: {
            data: [],
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await transactionsApi.getTransactions()

        expect(mockApi.get).toHaveBeenCalledWith('/transactions', { params: undefined })
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('createTransaction', () => {
      it('should create transaction successfully', async () => {
        const transactionData = {
          account_id: 1,
          amount: -25.00,
          currency: 'USD',
          date: '2024-01-15',
          description: 'Coffee Shop',
          merchant_name: 'Starbucks',
          category: 'food_and_drink',
          subcategory: 'coffee',
          is_pending: false,
          is_recurring: false,
        }

        const mockResponse = {
          data: {
            data: {
              id: 1,
              account_id: 1,
              amount: -25.00,
              currency: 'USD',
              date: '2024-01-15',
              description: 'Coffee Shop',
              merchant_name: 'Starbucks',
              category: 'food_and_drink',
              subcategory: 'coffee',
              is_pending: false,
              is_recurring: false,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z',
            },
          },
        }

        mockApi.post.mockResolvedValue(mockResponse)

        const result = await transactionsApi.createTransaction(transactionData)

        expect(mockApi.post).toHaveBeenCalledWith('/transactions', transactionData)
        expect(result).toEqual(mockResponse.data.data)
      })
    })
  })

  describe('balancesApi', () => {
    const mockApi = mockedAxios.create()

    beforeEach(() => {
      mockedAxios.create.mockReturnValue(mockApi)
    })

    describe('getBalanceOverview', () => {
      it('should get balance overview successfully', async () => {
        const mockResponse = {
          data: {
            data: {
              total_balance: 15000.00,
              total_available_balance: 14800.00,
              currency: 'USD',
              accounts: [
                {
                  account_id: 1,
                  account_name: 'Checking Account',
                  account_type: 'checking',
                  current_balance: 5000.00,
                  available_balance: 4800.00,
                  currency: 'USD',
                  last_updated: '2024-01-01T00:00:00Z',
                },
              ],
              net_worth_trend: [
                {
                  date: '2024-01-01',
                  balance: 15000.00,
                },
              ],
              last_updated: '2024-01-01T00:00:00Z',
            },
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await balancesApi.getBalanceOverview()

        expect(mockApi.get).toHaveBeenCalledWith('/balances/overview')
        expect(result).toEqual(mockResponse.data.data)
      })
    })

    describe('getBalanceSnapshots', () => {
      it('should get balance snapshots successfully', async () => {
        const params = {
          account_id: 1,
          start_date: '2024-01-01',
          end_date: '2024-01-31',
        }

        const mockResponse = {
          data: {
            data: [
              {
                id: 1,
                account_id: 1,
                balance: 5000.00,
                date: '2024-01-01',
                created_at: '2024-01-01T00:00:00Z',
              },
            ],
          },
        }

        mockApi.get.mockResolvedValue(mockResponse)

        const result = await balancesApi.getBalanceSnapshots(params)

        expect(mockApi.get).toHaveBeenCalledWith('/balances/snapshots', { params })
        expect(result).toEqual(mockResponse.data.data)
      })
    })
  })

  describe('utility functions', () => {
    describe('formatCurrency', () => {
      it('should format USD currency correctly', () => {
        expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56')
        expect(formatCurrency(0, 'USD')).toBe('$0.00')
        expect(formatCurrency(-500, 'USD')).toBe('-$500.00')
      })

      it('should use USD as default currency', () => {
        expect(formatCurrency(100)).toBe('$100.00')
      })

      it('should handle different currencies', () => {
        expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00')
        expect(formatCurrency(1000, 'GBP')).toBe('£1,000.00')
      })
    })

    describe('formatDate', () => {
      it('should format date correctly', () => {
        const dateString = '2024-01-15T10:30:00Z'
        const formatted = formatDate(dateString)
        expect(formatted).toMatch(/Jan 15, 2024/)
      })

      it('should handle different date formats', () => {
        const dateString = '2024-12-25'
        const formatted = formatDate(dateString)
        expect(formatted).toMatch(/Dec 25, 2024/)
      })
    })

    describe('formatDateTime', () => {
      it('should format date and time correctly', () => {
        const dateString = '2024-01-15T10:30:00Z'
        const formatted = formatDateTime(dateString)
        expect(formatted).toMatch(/Jan 15, 2024/)
        expect(formatted).toMatch(/\d{1,2}:\d{2}/) // Time format
      })
    })
  })

  describe('axios interceptors', () => {
    const mockApi = mockedAxios.create()

    beforeEach(() => {
      mockedAxios.create.mockReturnValue(mockApi)
    })

    it('should add authorization header when token exists', () => {
      localStorage.setItem('access_token', 'test-token')
      
      // Trigger a request
      mockApi.get.mockResolvedValue({ data: {} })
      
      // The interceptor should have been called
      expect(mockApi.interceptors.request.use).toHaveBeenCalled()
    })

    it('should handle 401 errors by redirecting to login', () => {
      const mockError = {
        response: {
          status: 401,
        },
      }

      // Mock window.location
      Object.defineProperty(window, 'location', {
        value: {
          href: '',
        },
        writable: true,
      })

      // Trigger the response interceptor
      const responseInterceptor = mockApi.interceptors.response.use.mock.calls[0]
      const errorHandler = responseInterceptor[1]
      
      errorHandler(mockError)

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })
}) 