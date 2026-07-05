# Super Admin Module Design Document

## Overview

The Super Admin module extends the existing Gym Management SaaS with platform-wide administrative capabilities while maintaining strict separation from existing gym-level functionality. The module introduces a new role hierarchy and creates dedicated interfaces for system oversight, all while preserving the existing multi-tenant architecture and JWT-based authentication system.

## Architecture

### Role-Based Access Control Enhancement

The existing User model already supports the `super_admin` role with nullable `gym_id` for platform administrators. The design leverages this existing architecture:

- **Super Admin Users**: `role='super_admin'`, `gym_id=null`
- **Existing Roles**: All existing gym-level roles remain unchanged
- **Authentication Flow**: Extends current JWT system with role-based route protection

### Multi-Tenant Data Access Patterns

The Super Admin module implements two data access patterns:

1. **Cross-Tenant Queries**: For analytics and platform-wide views (aggregated data)
2. **Tenant-Specific Actions**: For gym management operations (maintaining isolation)

### Route Structure

Super Admin routes will be prefixed with `/admin` to clearly separate from existing functionality:

```
/admin/dashboard          - Platform analytics dashboard
/admin/gyms              - Gym management interface
/admin/subscriptions     - Subscription management
/admin/users            - Cross-platform user management
/admin/settings         - System configuration
/admin/activity-logs    - Platform activity monitoring
```

## Components and Interfaces

### Backend Components

#### 1. Super Admin Authentication Middleware
```python
# New middleware function
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function
```

#### 2. Super Admin Routes Blueprint
- `backend/app/routes/admin.py` - New blueprint for all Super Admin endpoints
- Implements cross-tenant queries while respecting data privacy
- Provides aggregated analytics and management operations

#### 3. Enhanced Models for Super Admin Context
- Add new models: `SystemSettings`, `ActivityLog`, `GymSubscription`
- Extend existing models with Super Admin specific methods
- Maintain backward compatibility with existing model interfaces

#### 4. Analytics Service Layer
```python
# New service for platform analytics
class PlatformAnalyticsService:
    @staticmethod
    def get_platform_metrics():
        # Safe aggregation queries across tenants
    
    @staticmethod
    def get_gym_performance_data(gym_id):
        # Tenant-specific performance metrics
```

### Frontend Components

#### 1. Super Admin Layout Extension
- Extend existing `Layout` component to detect Super Admin role
- Conditionally render Super Admin sidebar items
- Maintain existing layout for non-Super Admin users

#### 2. Super Admin Sidebar Integration
```jsx
// Enhanced Sidebar component
const getSidebarLinks = (userRole) => {
  const baseLinks = [...existingLinks];
  
  if (userRole === 'super_admin') {
    return [
      ...baseLinks,
      { name: 'Platform Dashboard', path: '/admin/dashboard', icon: '🌐' },
      { name: 'Gym Management', path: '/admin/gyms', icon: '🏢' },
      { name: 'Subscriptions', path: '/admin/subscriptions', icon: '💳' },
      { name: 'User Management', path: '/admin/users', icon: '👤' },
      { name: 'System Settings', path: '/admin/settings', icon: '⚙️' },
      { name: 'Activity Logs', path: '/admin/logs', icon: '📋' }
    ];
  }
  
  return baseLinks;
};
```

#### 3. Super Admin Pages
- `SuperAdminDashboard.jsx` - Platform analytics and metrics
- `GymManagement.jsx` - Gym approval, suspension, deletion interface
- `SubscriptionManagement.jsx` - Platform-wide subscription oversight
- `UserManagement.jsx` - Cross-platform user administration
- `SystemSettings.jsx` - Platform configuration interface
- `ActivityLogs.jsx` - System activity monitoring

#### 4. Reusable Admin Components
- `AdminDataTable.jsx` - Consistent table component for admin views
- `AdminMetricCard.jsx` - Standardized metric display cards
- `AdminActionModal.jsx` - Confirmation modals for critical actions
- `AdminChart.jsx` - Analytics visualization components

## Data Models

### New Models

#### SystemSettings Model
```python
class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    setting_type = db.Column(db.String(20), nullable=False)  # string, number, boolean, json
    description = db.Column(db.Text, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### ActivityLog Model
```python
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)  # login, create, update, delete
    entity_type = db.Column(db.String(50), nullable=True)   # member, payment, gym, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

#### GymSubscription Model
```python
class GymSubscription(db.Model):
    __tablename__ = 'gym_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    monthly_price = db.Column(Numeric(10, 2), nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    features = db.Column(db.JSON, nullable=True)
    billing_cycle_start = db.Column(db.Date, nullable=False)
    billing_cycle_end = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')
    auto_renew = db.Column(db.Boolean, default=True)
```

### Enhanced Existing Models

#### Enhanced Gym Model
```python
# Add to existing Gym model
status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Suspended, Pending, Deleted
subscription_id = db.Column(db.Integer, db.ForeignKey('gym_subscriptions.id'), nullable=True)
approved_at = db.Column(db.DateTime, nullable=True)
approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
```

## Error Handling

### Super Admin Specific Error Handling

1. **Authorization Errors**
   - Clear error messages for insufficient privileges
   - Automatic logout on role verification failure
   - Audit logging for unauthorized access attempts

2. **Cross-Tenant Operation Safeguards**
   - Validation before any gym-affecting operations
   - Confirmation requirements for destructive actions
   - Rollback capabilities for reversible operations

3. **Data Integrity Protection**
   - Prevent accidental deletion of active gyms with members
   - Validate subscription changes don't break existing relationships
   - Maintain referential integrity during bulk operations

### Error Response Structure
```json
{
  "error": "Operation not permitted",
  "code": "SUPER_ADMIN_REQUIRED",
  "details": "This action requires Super Admin privileges",
  "timestamp": "2026-07-05T10:30:00Z"
}
```

## Testing Strategy

### Backend Testing

1. **Unit Tests**
   - Super Admin authentication middleware
   - Cross-tenant query safety
   - New model validation and relationships
   - Analytics calculation accuracy

2. **Integration Tests**
   - Super Admin route access control
   - Gym management workflow (approve → suspend → delete)
   - Subscription management operations
   - Activity logging functionality

3. **Security Tests**
   - Role-based access enforcement
   - JWT token validation with Super Admin claims
   - Cross-tenant data isolation verification
   - Audit trail completeness

### Frontend Testing

1. **Component Tests**
   - Super Admin sidebar rendering based on role
   - Admin-specific component functionality
   - Form validation and submission
   - Modal confirmation workflows

2. **Integration Tests**
   - Super Admin authentication flow
   - Navigation between admin sections
   - Data loading and display
   - Real-time metrics updates

3. **E2E Tests**
   - Complete Super Admin user journey
   - Gym management workflow
   - Cross-browser compatibility
   - Responsive design validation

### Test Data Strategy

1. **Test Fixtures**
   - Multi-gym test environment
   - Various user roles including Super Admin
   - Sample subscription and payment data
   - Realistic activity log entries

2. **Isolation Strategy**
   - Separate test database for Super Admin tests
   - Gym-specific test data isolation
   - Clean-up procedures for cross-tenant tests

## Security Considerations

### Authentication & Authorization

1. **Enhanced JWT Claims**
   - Include `is_super_admin` boolean in JWT payload
   - Validate Super Admin status on every admin route
   - Implement token refresh with role re-validation

2. **Route Protection**
   - Super Admin routes require explicit authorization
   - No fallback access for gym-level administrators
   - Clear separation between admin and gym interfaces

### Data Privacy & Compliance

1. **Cross-Tenant Data Access**
   - Aggregate data only (no individual member details)
   - Anonymized user information in platform analytics
   - GDPR-compliant data handling procedures

2. **Audit & Logging**
   - Complete audit trail for all Super Admin actions
   - Immutable activity logs with integrity verification
   - Retention policies for compliance requirements

### Operational Security

1. **Action Confirmation**
   - Multi-step confirmation for destructive operations
   - Email notifications for critical system changes
   - Rollback procedures for reversible actions

2. **Access Monitoring**
   - Real-time alerts for Super Admin login attempts
   - Geographic access pattern monitoring
   - Automated lockout for suspicious activities

## Implementation Phases

### Phase 1: Core Infrastructure
- Super Admin authentication and middleware
- Enhanced User model and JWT claims
- Basic Super Admin routes structure
- Frontend role detection and routing

### Phase 2: Gym Management
- Gym approval, suspension, and deletion functionality
- Enhanced Gym model with status tracking
- Gym management interface
- Activity logging for gym operations

### Phase 3: Analytics & Monitoring
- Platform analytics service layer
- Super Admin dashboard with metrics
- Activity log collection and display
- System performance monitoring

### Phase 4: Advanced Features
- Subscription management system
- User management across all gyms
- System settings configuration
- Advanced reporting and export capabilities

## Integration Points

### Existing System Integration

1. **Authentication System**
   - Extends existing JWT implementation
   - Maintains compatibility with gym-level authentication
   - No changes required to existing login flows

2. **Database Schema**
   - Additive changes only (no existing table modifications)
   - New foreign key relationships respect existing constraints
   - Backward compatibility maintained

3. **Frontend Architecture**
   - Extends existing routing and component structure
   - Preserves existing UI/UX patterns
   - Conditional rendering based on user role

### API Compatibility

1. **Existing Endpoints**
   - No modifications to existing gym-level APIs
   - Maintained response formats and error codes
   - Existing client integrations unaffected

2. **New Endpoints**
   - Clear `/admin` prefix for all Super Admin endpoints
   - Consistent with existing API patterns
   - Comprehensive documentation and examples