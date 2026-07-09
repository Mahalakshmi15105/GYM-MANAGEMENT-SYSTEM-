# Design Document

## Overview

The Member Login and Dashboard system extends the existing authentication architecture to support member users alongside gym owners. This implementation leverages the existing JWT-based authentication system, role-based routing, and multi-tenant architecture while adding member-specific functionality.

## Architecture

### Authentication Flow
- **Existing Flow**: Gym owners authenticate via `/api/auth/login` 
- **New Flow**: Members authenticate via the same endpoint with role differentiation
- **Role Detection**: Login response includes user role (`gym_owner` or `member`)
- **Session Management**: JWT tokens contain role information for route protection

### Multi-tenant Isolation
- Members are scoped to their gym via `gym_id` in the database
- All member operations maintain tenant isolation
- Member sessions include both `member_id` and `gym_id` in JWT payload

## Components and Interfaces

### Backend Components

#### 1. Enhanced Authentication (auth.py)
```python
# Enhanced login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    # Determine if credentials match gym owner or member
    # Return role-specific JWT token and user data
    
# Member-specific authentication utilities
def authenticate_member(email, password, gym_id)
def generate_member_jwt(member_id, gym_id)
```

#### 2. Member Route Protection
```python
# New decorator for member-only routes
def member_required(f):
    # Validate JWT contains member role
    # Extract member_id and gym_id from token
```

#### 3. First-time Login Detection
```python
# Password change tracking
def is_first_login(member):
    return not member.password_changed

def mark_password_changed(member_id):
    # Update password_changed field to True
```

### Frontend Components

#### 1. Enhanced Login Page
- Role selection or auto-detection
- Unified login form handling both gym owners and members
- Role-specific error messaging

#### 2. Member Dashboard (MemberDashboard.jsx)
```jsx
const MemberDashboard = () => {
  // Display member-specific information
  // Navigation to member features
  // Password change functionality
  // Logout capability
};
```

#### 3. Member Password Change (MemberChangePassword.jsx)
```jsx
const MemberChangePassword = () => {
  // Force password change on first login
  // Prevent navigation until password changed
  // Update password_changed status
};
```

#### 4. Enhanced Route Protection (ProtectedRoute.jsx)
```jsx
const ProtectedRoute = ({ allowedRoles, children }) => {
  // Check user role against allowed roles
  // Redirect based on role and authentication status
};
```

#### 5. Public Route Redirection (PublicOnlyRoute.jsx)
```jsx
const PublicOnlyRoute = ({ children }) => {
  // Redirect authenticated users to appropriate dashboard
  // Role-based dashboard routing
};
```

## Data Models

### Enhanced Member Model
```python
class Member:
    id = Integer (Primary Key)
    gym_id = Integer (Foreign Key to Gym)
    email = String (Unique within gym)
    password_hash = String
    password_changed = Boolean (Default: False)  # New field
    name = String
    membership_plan_id = Integer (Foreign Key)
    # ... existing fields
```

### JWT Payload Structure
```json
{
  "user_id": "member_123 or gym_456",
  "role": "member or gym_owner", 
  "gym_id": "123",
  "exp": "expiration_timestamp"
}
```

## Error Handling

### Authentication Errors
- Invalid credentials: Role-specific error messages
- Account not found: Clear indication of role-based lookup failure
- First-time login: Automatic redirect to password change

### Authorization Errors  
- Role mismatch: Clear error message indicating required role
- Unauthorized access: Redirect to appropriate login or dashboard

### Session Errors
- Expired tokens: Automatic redirect to login with context preservation
- Invalid tokens: Clear session and redirect to login

## Testing Strategy

### Unit Tests
- Member authentication functions
- JWT token generation and validation
- Password change workflows
- Role-based access control

### Integration Tests
- Complete login flows for both roles
- First-time login password change flow
- Cross-role access prevention
- Session management across role transitions

### End-to-End Tests
- Member login → dashboard → password change → logout flow
- Role-based route protection verification
- Public route redirection for authenticated users