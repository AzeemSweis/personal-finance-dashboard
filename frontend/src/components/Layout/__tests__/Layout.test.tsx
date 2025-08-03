import React from 'react';
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../../../stores/authStore';
import Layout from '../Layout';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock the auth store
jest.mock('../../../stores/authStore', () => ({
  useAuthStore: jest.fn(),
}));

// Mock child components
jest.mock('../Sidebar', () => {
  return function MockSidebar() {
    return <div data-testid="sidebar">Sidebar</div>;
  };
});

jest.mock('../Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>;
  };
});

const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('Layout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render only children for login page', () => {
    mockUseRouter.mockReturnValue({
      pathname: '/login',
    } as any);
    
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
    } as any);

    render(
      <Layout>
        <div data-testid="login-content">Login Page</div>
      </Layout>
    );

    expect(screen.getByTestId('login-content')).toBeInTheDocument();
    expect(screen.queryByTestId('sidebar')).not.toBeInTheDocument();
    expect(screen.queryByTestId('header')).not.toBeInTheDocument();
  });

  it('should render only children for register page', () => {
    mockUseRouter.mockReturnValue({
      pathname: '/register',
    } as any);
    
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
    } as any);

    render(
      <Layout>
        <div data-testid="register-content">Register Page</div>
      </Layout>
    );

    expect(screen.getByTestId('register-content')).toBeInTheDocument();
    expect(screen.queryByTestId('sidebar')).not.toBeInTheDocument();
    expect(screen.queryByTestId('header')).not.toBeInTheDocument();
  });

  it('should render only children when not authenticated', () => {
    mockUseRouter.mockReturnValue({
      pathname: '/dashboard',
    } as any);
    
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
    } as any);

    render(
      <Layout>
        <div data-testid="unauthenticated-content">Please log in</div>
      </Layout>
    );

    expect(screen.getByTestId('unauthenticated-content')).toBeInTheDocument();
    expect(screen.queryByTestId('sidebar')).not.toBeInTheDocument();
    expect(screen.queryByTestId('header')).not.toBeInTheDocument();
  });

  it('should render full layout when authenticated', () => {
    mockUseRouter.mockReturnValue({
      pathname: '/dashboard',
    } as any);
    
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
    } as any);

    render(
      <Layout>
        <div data-testid="dashboard-content">Dashboard</div>
      </Layout>
    );

    expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });
});