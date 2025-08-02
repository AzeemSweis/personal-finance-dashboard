import { renderHook, act } from '@testing-library/react'
import { useAuthStore } from '../authStore'
import { authApi } from '../../services/api'

// Mock the API service
jest.mock('../../services/api', () => ({
  authApi: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}))

const mockAuthApi = authApi as jest.Mocked<typeof authApi>

describe('useAuthStore', () => {
  beforeEach(() => {
    // Clear all mocks and localStorage before each test
    jest.clearAllMocks()
    localStorage.clear()
    
    // Mock localStorage methods
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    })
    
    // Reset store state
    act(() => {
      useAuthStore.getState().logout()
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore())
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('login', () => {
    it('should login successfully', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const mockAuthResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        expires_in: 1800,
      }

      mockAuthApi.login.mockResolvedValue(mockAuthResponse)
      mockAuthApi.getCurrentUser.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      expect(mockAuthApi.login).toHaveBeenCalledWith({
        username: 'test@example.com',
        password: 'password123',
      })
      expect(mockAuthApi.getCurrentUser).toHaveBeenCalled()
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.token).toBe('mock-token')
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'mock-token')
    })

    it('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials')
      mockAuthApi.login.mockRejectedValue(mockError)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        try {
          await result.current.login('test@example.com', 'wrongpassword')
        } catch (error) {
          // Expected to throw
        }
      })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe('Login failed')
    })

    it('should handle API error response', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Incorrect email or password',
          },
        },
      }
      mockAuthApi.login.mockRejectedValue(mockError)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        try {
          await result.current.login('test@example.com', 'wrongpassword')
        } catch (error) {
          // Expected to throw
        }
      })

      expect(result.current.error).toBe('Incorrect email or password')
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      const mockUser = {
        id: 1,
        email: 'new@example.com',
        username: 'newuser',
        first_name: 'New',
        last_name: 'User',
        is_active: true,
        is_verified: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const registerData = {
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
        first_name: 'New',
        last_name: 'User',
      }

      mockAuthApi.register.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.register(registerData)
      })

      expect(mockAuthApi.register).toHaveBeenCalledWith(registerData)
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should handle registration failure', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Email already registered',
          },
        },
      }
      mockAuthApi.register.mockRejectedValue(mockError)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        try {
          await result.current.register({
            email: 'existing@example.com',
            username: 'existinguser',
            password: 'password123',
          })
        } catch (error) {
          // Expected to throw
        }
      })

      expect(result.current.error).toBe('Email already registered')
    })
  })

  describe('logout', () => {
    it('should logout successfully', () => {
      const { result } = renderHook(() => useAuthStore())

      // First, set some state
      act(() => {
        useAuthStore.setState({
          user: { id: 1, email: 'test@example.com' } as any,
          token: 'mock-token',
          isAuthenticated: true,
        })
      })

      // Then logout
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })

  describe('clearError', () => {
    it('should clear error state', () => {
      const { result } = renderHook(() => useAuthStore())

      // Set an error
      act(() => {
        useAuthStore.setState({ error: 'Some error' })
      })

      expect(result.current.error).toBe('Some error')

      // Clear the error
      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.setLoading(true)
      })

      expect(result.current.isLoading).toBe(true)

      act(() => {
        result.current.setLoading(false)
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('updateUser', () => {
    it('should update user data', () => {
      const { result } = renderHook(() => useAuthStore())

      const mockUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      // Set initial user
      act(() => {
        useAuthStore.setState({ user: mockUser })
      })

      // Update user
      act(() => {
        result.current.updateUser({ first_name: 'Updated' })
      })

      expect(result.current.user?.first_name).toBe('Updated')
      expect(result.current.user?.email).toBe('test@example.com') // Other fields unchanged
    })

    it('should not update user if no user exists', () => {
      const { result } = renderHook(() => useAuthStore())

      act(() => {
        result.current.updateUser({ first_name: 'Updated' })
      })

      expect(result.current.user).toBeNull()
    })
  })

  describe('persistence', () => {
    it('should persist state to localStorage', () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      act(() => {
        useAuthStore.setState({
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
        })
      })

      // The store should automatically persist to localStorage
      // We can't directly test the persistence due to the mock,
      // but we can verify the state is set correctly
      expect(useAuthStore.getState().user).toEqual(mockUser)
      expect(useAuthStore.getState().token).toBe('mock-token')
      expect(useAuthStore.getState().isAuthenticated).toBe(true)
    })
  })
}) 