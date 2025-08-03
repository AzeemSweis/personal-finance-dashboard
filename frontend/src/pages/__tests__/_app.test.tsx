import React from 'react';
import { render } from '@testing-library/react';
import { useAuthStore, initializeAuth } from '../../stores/authStore';
import MyApp from '../_app';

// Mock the auth store
jest.mock('../../stores/authStore', () => ({
  useAuthStore: jest.fn(),
  initializeAuth: jest.fn(),
}));

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockInitializeAuth = initializeAuth as jest.MockedFunction<typeof initializeAuth>;

// Mock component
const MockComponent = (props: any) => <div data-testid="mock-component">Mock Component</div>;

describe('MyApp', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the component', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
    } as any);

    const { getByTestId } = render(
      <MyApp 
        Component={MockComponent} 
        pageProps={{}} 
        router={{} as any}
      />
    );

    expect(getByTestId('mock-component')).toBeInTheDocument();
  });

  it('should call initializeAuth on mount', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
    } as any);

    render(
      <MyApp 
        Component={MockComponent} 
        pageProps={{}} 
        router={{} as any}
      />
    );

    expect(mockInitializeAuth).toHaveBeenCalledTimes(1);
  });

  it('should work when authenticated', () => {
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
    } as any);

    const { getByTestId } = render(
      <MyApp 
        Component={MockComponent} 
        pageProps={{}} 
        router={{} as any}
      />
    );

    expect(getByTestId('mock-component')).toBeInTheDocument();
  });
});