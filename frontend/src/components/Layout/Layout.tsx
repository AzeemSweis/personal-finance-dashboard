import React, { ReactNode } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../../stores/authStore';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  // Don't show layout for auth pages
  const isAuthPage = router.pathname === '/login' || router.pathname === '/register';

  if (isAuthPage) {
    return <div className="min-h-screen bg-gray-50">{children}</div>;
  }

  if (!isAuthenticated) {
    return <div className="min-h-screen bg-gray-50">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header />
          
          {/* Main content area */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50">
            <div className="container mx-auto px-4 py-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout; 