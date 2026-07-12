import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../context/AuthContext';
import Sidebar from '../Sidebar';

// Mock the useAuth hook
const mockAuth = {
  user: null,
  logout: jest.fn(),
  isSuperAdmin: false,
  canAccessGymManagement: false
};

jest.mock('../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => mockAuth
}));

const TestSidebar = (props) => (
  <BrowserRouter>
    <Sidebar isOpen={true} setIsOpen={jest.fn()} {...props} />
  </BrowserRouter>
);

describe('Sidebar', () => {
  beforeEach(() => {
    // Reset mock auth state
    mockAuth.user = null;
    mockAuth.isSuperAdmin = false;
    mockAuth.canAccessGymManagement = false;
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render the SmartGoNext Gym brand', () => {
      render(<TestSidebar />);
      
      expect(screen.getByText('🏋️‍♂️')).toBeInTheDocument();
      expect(screen.getByText('SmartGoNext Gym')).toBeInTheDocument();
    });

    it('should always render the Dashboard link', () => {
      render(<TestSidebar />);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  describe('Super Admin Navigation', () => {
    beforeEach(() => {
      mockAuth.user = { id: 1, name: 'Super Admin', role: 'super_admin' };
      mockAuth.isSuperAdmin = true;
      mockAuth.canAccessGymManagement = true;
    });

    it('should render Super Admin navigation links', () => {
      render(<TestSidebar />);
      
      // Super Admin specific links
      expect(screen.getByText('Platform Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Gym Management')).toBeInTheDocument();
      expect(screen.getByText('User Management')).toBeInTheDocument();
      expect(screen.getByText('System Settings')).toBeInTheDocument();
      expect(screen.getByText('Activity Logs')).toBeInTheDocument();
    });

    it('should NOT render gym management links for Super Admin', () => {
      render(<TestSidebar />);
      
      // Should NOT have gym management links
      expect(screen.queryByText('Members')).not.toBeInTheDocument();
      expect(screen.queryByText('Membership Plans')).not.toBeInTheDocument();
      expect(screen.queryByText('Payments')).not.toBeInTheDocument();
      expect(screen.queryByText('Attendance')).not.toBeInTheDocument();
      expect(screen.queryByText('Trainers & Plans')).not.toBeInTheDocument();
      expect(screen.queryByText('Gym Profile')).not.toBeInTheDocument();
      expect(screen.queryByText('Settings')).not.toBeInTheDocument();
    });

    it('should show admin badge in user profile', () => {
      render(<TestSidebar />);
      
      expect(screen.getByText('Admin')).toBeInTheDocument();
    });

    it('should use red styling for super admin avatar', () => {
      render(<TestSidebar />);
      
      const avatar = screen.getByText('S'); // First letter of "Super Admin"
      expect(avatar).toBeInTheDocument();
      // The avatar div should have the classes
      const avatarDiv = avatar.closest('div.w-10.h-10');
      expect(avatarDiv).toHaveClass('bg-red-100', 'border-red-200', 'text-red-600');
    });
  });

  describe('Gym Owner Navigation', () => {
    beforeEach(() => {
      mockAuth.user = { id: 2, name: 'Gym Owner', role: 'gym_owner', gym_id: 1 };
      mockAuth.isSuperAdmin = false;
      mockAuth.canAccessGymManagement = true;
    });

    it('should render gym management links but not super admin links', () => {
      render(<TestSidebar />);
      
      // Should have gym management links
      expect(screen.getByText('Members')).toBeInTheDocument();
      expect(screen.getByText('Membership Plans')).toBeInTheDocument();
      expect(screen.getByText('Payments')).toBeInTheDocument();
      
      // Should NOT have super admin links
      expect(screen.queryByText('Platform Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('User Management')).not.toBeInTheDocument();
      expect(screen.queryByText('System Settings')).not.toBeInTheDocument();
    });

    it('should not show admin badge', () => {
      render(<TestSidebar />);
      
      expect(screen.queryByText('Admin')).not.toBeInTheDocument();
    });

    it('should use orange styling for gym owner avatar', () => {
      render(<TestSidebar />);
      
      const avatar = screen.getByText('G'); // First letter of "Gym Owner"
      expect(avatar).toBeInTheDocument();
      // The avatar div should have the classes
      const avatarDiv = avatar.closest('div.w-10.h-10');
      expect(avatarDiv).toHaveClass('bg-orange-100', 'border-orange-200', 'text-orange-600');
    });
  });

  describe('Member Navigation', () => {
    beforeEach(() => {
      mockAuth.user = { id: 3, name: 'Member', role: 'member', gym_id: 1 };
      mockAuth.isSuperAdmin = false;
      mockAuth.canAccessGymManagement = false;
    });

    it('should only render dashboard for members', () => {
      render(<TestSidebar />);
      
      // Should have dashboard
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      
      // Should NOT have gym management or admin links
      expect(screen.queryByText('Members')).not.toBeInTheDocument();
      expect(screen.queryByText('Platform Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('User Management')).not.toBeInTheDocument();
    });
  });

  describe('User Profile Section', () => {
    it('should display user information', () => {
      mockAuth.user = { id: 1, name: 'John Doe', role: 'gym_owner' };
      
      render(<TestSidebar />);
      
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('gym owner')).toBeInTheDocument();
    });

    it('should handle user with no name', () => {
      mockAuth.user = { id: 1, role: 'member' };
      
      render(<TestSidebar />);
      
      expect(screen.getByText('U')).toBeInTheDocument(); // Default initial
    });

    it('should call logout when logout button is clicked', () => {
      mockAuth.user = { id: 1, name: 'Test User', role: 'member' };
      
      render(<TestSidebar />);
      
      const logoutButton = screen.getByText('Log Out');
      fireEvent.click(logoutButton);
      
      expect(mockAuth.logout).toHaveBeenCalled();
    });
  });

  describe('Mobile Functionality', () => {
    it('should call setIsOpen when close button is clicked', () => {
      const setIsOpen = jest.fn();
      mockAuth.user = { id: 1, name: 'Test User', role: 'member' };
      
      render(<TestSidebar setIsOpen={setIsOpen} />);
      
      const closeButton = screen.getByText('✕');
      fireEvent.click(closeButton);
      
      expect(setIsOpen).toHaveBeenCalledWith(false);
    });

    it('should call setIsOpen when navigation link is clicked', () => {
      const setIsOpen = jest.fn();
      mockAuth.user = { id: 1, name: 'Test User', role: 'gym_owner' };
      mockAuth.canAccessGymManagement = true;
      
      render(<TestSidebar setIsOpen={setIsOpen} />);
      
      const dashboardLink = screen.getByText('Dashboard');
      fireEvent.click(dashboardLink);
      
      expect(setIsOpen).toHaveBeenCalledWith(false);
    });
  });

  describe('Sidebar Visibility', () => {
    it('should be visible when isOpen is true', () => {
      render(<TestSidebar isOpen={true} />);
      
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('translate-x-0');
    });

    it('should be hidden when isOpen is false', () => {
      render(<TestSidebar isOpen={false} />);
      
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('-translate-x-full');
    });
  });
});