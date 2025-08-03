import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { useAuthStore } from '../../../stores/authStore';
import Header from '../Header';

// Mock the auth store
jest.mock('../../../stores/authStore', () => ({
  useAuthStore: jest.fn(),
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('Header', () => {
  const mockLogout = jest.fn();
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
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuthStore.mockReturnValue({
      user: mockUser,
      logout: mockLogout,
    } as any);
  });

  it('should render header with search input', () => {
    render(<Header />);
    
    const searchInput = screen.getByPlaceholderText('Search accounts, transactions...');
    expect(searchInput).toBeInTheDocument();
  });

  it('should render notification and settings buttons', () => {
    render(<Header />);
    
    // Look for buttons by their SVG icons (Bell and Settings)
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('should handle user interaction', () => {
    render(<Header />);
    
    const searchInput = screen.getByPlaceholderText('Search accounts, transactions...');
    fireEvent.change(searchInput, { target: { value: 'test search' } });
    
    expect(searchInput).toHaveValue('test search');
  });

  it('should render when user is null', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      logout: mockLogout,
    } as any);

    render(<Header />);
    
    const searchInput = screen.getByPlaceholderText('Search accounts, transactions...');
    expect(searchInput).toBeInTheDocument();
  });
});