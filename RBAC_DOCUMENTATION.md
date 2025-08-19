# Role-Based Access Control (RBAC) System Documentation

## Overview

The auto repair shop system now implements a comprehensive role-based access control system with three distinct user types, each having different privilege levels and access permissions.

## User Roles

### 1. Owner (Highest Privilege)
**Role**: `owner`
**Description**: Shop owners have full administrative control over the system.

**Permissions**:
- ✅ **Full Shop Management**: Create, view, update, delete shops
- ✅ **Employee Management**: Create, view, update, delete employee accounts
- ✅ **User Management**: View all users, update user roles
- ✅ **Financial Data Access**: View revenue, profits, financial summaries
- ✅ **Inventory Management**: Manage parts and services across all shops
- ✅ **Order Management**: View and manage all repair orders
- ✅ **Customer Data**: Access all customer information
- ✅ **Appointment Management**: Full CRUD operations on appointments

**API Endpoints Available**:
- `GET /api/admin/users/` - List all users
- `PUT /api/admin/users/{id}/role/` - Update user roles
- `GET /api/shop/financial_summary/` - Financial data
- All shop, employee, customer, and repair order endpoints

### 2. Employee (Medium Privilege)
**Role**: `employee`  
**Description**: Shop employees can perform day-to-day operations.

**Permissions**:
- ❌ **Shop Management**: Cannot create/delete shops (view only their shop)
- ❌ **Employee Management**: Cannot create/delete employee accounts
- ❌ **Financial Data**: Cannot view revenue/profit data
- ✅ **Inventory Management**: Manage parts and services for their shop
- ✅ **Order Management**: Create and manage repair orders
- ✅ **Customer Data**: Access customer information
- ✅ **Appointment Management**: Full CRUD operations on appointments

**API Endpoints Available**:
- Shop endpoints (filtered to their shop only)
- Service and Parts endpoints (their shop only)
- Customer and Vehicle endpoints
- Repair Order creation and management
- Appointment management

### 3. Customer (Lowest Privilege)
**Role**: `customer`
**Description**: Customers can only access their own data and create appointments.

**Permissions**:
- ❌ **Shop Management**: No access to shop data
- ❌ **Employee Management**: No access
- ❌ **Financial Data**: No access
- ❌ **Inventory Management**: No access to parts/services management
- ❌ **All Orders**: Cannot view other customers' orders
- ✅ **Own Data**: View and update their own profile
- ✅ **Own Vehicles**: View their vehicles
- ✅ **Own Orders**: View their repair orders only
- ✅ **Appointments**: Create appointments for their vehicles

**API Endpoints Available**:
- `GET /api/auth/user/` - Own profile
- `PUT /api/auth/user/update/` - Update own profile
- Customer endpoints (filtered to own data)
- Vehicle endpoints (own vehicles only)
- Repair Orders (own orders only)
- Appointment creation

## Implementation Details

### User Model Extensions

```python
class User(AbstractUser):
    OWNER = 'owner'
    EMPLOYEE = 'employee'
    CUSTOMER = 'customer'
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default=CUSTOMER)
    
    @property
    def is_owner(self):
        return self.role == self.OWNER
    
    @property
    def can_manage_shops(self):
        return self.is_owner
    
    # ... additional permission properties
```

### Custom Permission Classes

1. **IsOwner**: Only owners can access
2. **IsOwnerOrEmployee**: Owners and employees can access
3. **CanManageShops**: Shop management permissions
4. **CanViewFinancialData**: Financial data access
5. **IsCustomerOwnerOfObject**: Customers can only access their own data

### API Endpoint Security

#### Authentication URLs
- `POST /api/auth/register/` - Public (customers by default)
- `POST /api/auth/login/` - Public
- `GET /api/auth/user/` - Authenticated users (role-based response)

#### Admin URLs (Owner Only)
- `GET /api/admin/users/` - List all users
- `PUT /api/admin/users/{id}/role/` - Update user roles

#### Shop Management (Owner Only)
- `GET|POST|PUT|DELETE /api/shop/` - Full CRUD operations

#### Inventory Management (Owner + Employee)
- `GET|POST|PUT|DELETE /api/services/` - Service management
- `GET|POST|PUT|DELETE /api/parts/` - Parts management
- `GET /api/parts/low_stock/` - Low stock alerts

#### Order Management
- **Owner/Employee**: Full access to all orders
- **Customer**: Only their own orders
- `GET /api/orders/financial_summary/` - Owner only

#### Customer Data
- **Owner/Employee**: All customers
- **Customer**: Own profile only

## Data Filtering by Role

### QuerySet Filtering
Each ViewSet implements role-based queryset filtering:

```python
def get_queryset(self):
    user = self.request.user
    if user.is_owner:
        return Model.objects.all()
    elif user.is_employee:
        return Model.objects.filter(shop=user.employee_profile.shop)
    elif user.is_customer:
        return Model.objects.filter(customer=user.customer_profile)
    return Model.objects.none()
```

## User Registration Flow

### Customer Registration
- Anyone can register as a customer (default role)
- Email verification required
- Automatic role assignment: `customer`

### Employee/Owner Creation
- Only existing owners can create employee/owner accounts
- Role validation in serializer
- Admin interface for role management

## Testing the System

### Sample Users Created
```
Owner: mike.manager@autorepair.com (password: password123)
Employee: john.mechanic@autorepair.com (password: password123)  
Customer: alice.cooper@customer.com (password: password123)
```

### API Testing Examples

#### 1. Login as Owner
```bash
POST /api/token/
{
  "email": "mike.manager@autorepair.com",
  "password": "password123"
}
```

#### 2. Access User Profile
```bash
GET /api/auth/user/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "email": "mike.manager@autorepair.com",
  "role": "owner",
  "permissions": {
    "can_manage_shops": true,
    "can_view_financial_data": true,
    "is_owner": true
  }
}
```

#### 3. Owner - List All Users
```bash
GET /api/admin/users/
Authorization: Bearer {owner_token}
```

#### 4. Employee - View Inventory
```bash
GET /api/services/
Authorization: Bearer {employee_token}
# Returns services for employee's shop only
```

#### 5. Customer - View Own Orders
```bash
GET /api/orders/
Authorization: Bearer {customer_token}
# Returns only customer's own repair orders
```

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Role Validation**: Server-side role verification
3. **Data Isolation**: Users can only access appropriate data
4. **Permission Inheritance**: Owners inherit all lower-level permissions
5. **Audit Trail**: All role changes and access attempts are logged

## Frontend Integration

### Role-Based UI Rendering
The frontend can use the `permissions` object from the user profile to conditionally render UI elements:

```javascript
// Example React component
const Dashboard = ({ user }) => {
  return (
    <div>
      {user.permissions.can_manage_shops && <ShopManagement />}
      {user.permissions.can_view_financial_data && <FinancialReports />}
      {user.permissions.can_manage_inventory && <InventoryManagement />}
      {user.is_customer && <CustomerDashboard />}
    </div>
  );
};
```

### Route Protection
```javascript
// Protected route example
const ProtectedRoute = ({ component: Component, requiredRole, ...rest }) => {
  const { user } = useAuth();
  
  return (
    <Route
      {...rest}
      render={(props) =>
        user && user.role === requiredRole ? (
          <Component {...props} />
        ) : (
          <Redirect to="/unauthorized" />
        )
      }
    />
  );
};
```

## Migration Guide

### Existing Users
All existing users will default to `customer` role. Use the admin interface or API to update roles as needed:

```bash
PUT /api/admin/users/{user_id}/role/
{
  "role": "owner"  # or "employee"
}
```

### Database Changes
The migration adds a `role` field to the User model with a default value of `customer`.

## Security Best Practices

1. **Never trust frontend role checks** - Always validate on the backend
2. **Use HTTPS** in production for secure token transmission
3. **Implement proper CORS** settings for cross-origin requests
4. **Regular security audits** of permission assignments
5. **Monitor suspicious access patterns**

## Future Enhancements

1. **Multi-shop ownership**: Allow owners to own multiple shops
2. **Advanced employee roles**: Mechanic, receptionist, manager sub-roles
3. **Temporary permissions**: Grant temporary elevated access
4. **API rate limiting**: Role-based rate limiting
5. **Activity logging**: Detailed audit logs for all actions
