# Security Implementation Guide

## Overview

This document describes the authentication and security features implemented in OmniScope AI, including OAuth2/OIDC authentication, multi-factor authentication (MFA), role-based access control (RBAC), audit logging, data encryption, and anonymization.

## Features Implemented

### 1. OAuth2/OIDC Authentication Service

**Location**: `backend_db/auth.py`, `modules/auth_module.py`

**Features**:
- JWT token generation and validation
- Refresh token mechanism
- Secure password hashing with bcrypt
- Token expiration and renewal
- Session management

**Endpoints**:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and revoke token
- `POST /api/auth/logout-all` - Logout from all devices
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

**Configuration**:
```bash
# Set in environment variables
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. Multi-Factor Authentication (MFA)

**Location**: `backend_db/mfa.py`, `modules/auth_module.py`

**Features**:
- TOTP-based MFA using pyotp
- QR code generation for authenticator apps
- Recovery codes for account recovery
- MFA setup and verification flow

**Endpoints**:
- `POST /api/auth/mfa/setup` - Initialize MFA setup
- `POST /api/auth/mfa/enable` - Enable MFA after verification
- `POST /api/auth/mfa/disable` - Disable MFA
- `POST /api/auth/mfa/verify` - Complete MFA login
- `GET /api/auth/mfa/recovery-codes/count` - Get unused recovery codes count
- `POST /api/auth/mfa/recovery-codes/regenerate` - Regenerate recovery codes

**Usage Flow**:
1. User calls `/mfa/setup` to get QR code and recovery codes
2. User scans QR code with authenticator app (Google Authenticator, Authy, etc.)
3. User calls `/mfa/enable` with TOTP token to enable MFA
4. On subsequent logins, user must provide TOTP token via `/mfa/verify`

### 3. Role-Based Access Control (RBAC)

**Location**: `backend_db/rbac.py`, `modules/rbac_module.py`

**Default Roles**:
- **Admin**: Full system access
- **PI** (Principal Investigator): Project and team management
- **Researcher**: Analysis and pipeline creation
- **Analyst**: Data viewing and analysis
- **Viewer**: Read-only access

**Permission Categories**:
- User management
- Role management
- Data management
- Pipeline management
- Model management
- Results and analysis
- Workspace management
- Plugin management
- Audit and compliance
- System administration

**Endpoints**:
- `GET /api/rbac/roles` - List all roles
- `GET /api/rbac/roles/{role_id}` - Get role details
- `POST /api/rbac/roles` - Create new role
- `PUT /api/rbac/roles/{role_id}` - Update role
- `DELETE /api/rbac/roles/{role_id}` - Delete role
- `POST /api/rbac/users/assign-role` - Assign role to user
- `POST /api/rbac/users/remove-role` - Remove role from user
- `GET /api/rbac/users/{user_id}/permissions` - Get user permissions
- `GET /api/rbac/permissions/available` - List all permissions
- `GET /api/rbac/me/permissions` - Get current user permissions

**Usage in Code**:
```python
from backend_db.rbac import require_permission, Permissions

# Require specific permission
@router.get("/endpoint", dependencies=[Depends(require_permission(Permissions.DATA_READ))])
async def protected_endpoint():
    pass

# Or use in function
async def my_function(
    current_user: User = Depends(require_permission(Permissions.PIPELINE_CREATE))
):
    pass
```

### 4. Audit Logging System

**Location**: `backend_db/audit.py`, `modules/audit_module.py`

**Features**:
- Immutable append-only logs
- Captures user actions, IP addresses, timestamps
- Searchable and filterable logs
- Compliance reporting

**Endpoints**:
- `GET /api/audit/logs` - Get audit logs with filters
- `GET /api/audit/logs/user/{user_id}` - Get user's audit logs
- `GET /api/audit/logs/resource/{resource}/{resource_id}` - Get resource audit logs
- `GET /api/audit/logs/failed` - Get failed actions
- `GET /api/audit/compliance/report` - Generate compliance report
- `GET /api/audit/me/activity` - Get current user's activity

**Logged Actions**:
- Authentication (login, logout, MFA)
- User management
- Role assignments
- Data access and modifications
- Pipeline operations
- Model training
- Configuration changes

### 5. Data Encryption Services

**Location**: `backend_db/encryption.py`

**Features**:
- AES-256 encryption for sensitive data
- Key derivation using PBKDF2
- Field-level encryption
- Secure key management

**Configuration**:
```bash
# Set in environment variables
ENCRYPTION_MASTER_KEY=your-encryption-key-here
```

**Usage**:
```python
from backend_db.encryption import encrypt_data, decrypt_data, hash_data

# Encrypt sensitive data
encrypted = encrypt_data("sensitive information")

# Decrypt data
decrypted = decrypt_data(encrypted)

# One-way hash
hashed = hash_data("data to hash")
```

### 6. Data Anonymization Engine

**Location**: `backend_db/anonymization.py`, `modules/anonymization_module.py`

**Features**:
- PII detection using regex patterns
- Multiple anonymization methods (hashing, masking, generalization)
- K-anonymity checking
- GDPR compliance (right to erasure, data portability)

**Supported PII Types**:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses
- Dates of birth
- Postal codes
- Medical record numbers
- And more...

**Endpoints**:
- `POST /api/anonymization/detect-pii` - Detect PII in text
- `POST /api/anonymization/anonymize-text` - Anonymize text
- `POST /api/anonymization/anonymize-dataset` - Anonymize dataset
- `POST /api/anonymization/check-k-anonymity` - Check k-anonymity
- `POST /api/anonymization/gdpr/delete-user-data` - Delete user data (GDPR)
- `GET /api/anonymization/gdpr/user-data-export/{user_id}` - Export user data (GDPR)

**Anonymization Methods**:
- **Hashing**: One-way hash of data
- **Masking**: Replace characters with asterisks
- **Generalization**: Reduce precision (e.g., age bins, date to year)
- **Removal**: Complete removal of sensitive data

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```bash
# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_MASTER_KEY=your-encryption-key-here

# Admin User (for initial setup)
ADMIN_EMAIL=admin@omniscope.ai
ADMIN_PASSWORD=change-this-password

# Database
DATABASE_URL=sqlite:///./db/backend.db

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Initialize Database

```bash
python scripts/init-security-db.py
```

This will:
- Create all database tables
- Create default roles (Admin, PI, Researcher, Analyst, Viewer)
- Create an admin user with credentials from environment variables

### 4. Start the Application

```bash
python main.py
```

The API will be available at `http://localhost:8001`

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Security Best Practices

### Production Deployment

1. **Change Default Credentials**: Immediately change the default admin password
2. **Use Strong Keys**: Generate strong random keys for SECRET_KEY and ENCRYPTION_MASTER_KEY
3. **Enable HTTPS**: Use TLS 1.3 for all endpoints
4. **Set Secure Headers**: Configure CORS, CSP, and other security headers
5. **Rate Limiting**: Implement rate limiting on authentication endpoints
6. **Monitor Logs**: Regularly review audit logs for suspicious activity
7. **Backup Keys**: Securely backup encryption keys
8. **Key Rotation**: Implement periodic key rotation

### Key Generation

```python
# Generate SECRET_KEY
import secrets
print(secrets.token_urlsafe(32))

# Generate ENCRYPTION_MASTER_KEY
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Password Requirements

Implement password requirements in your application:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### MFA Recommendations

- Require MFA for admin accounts
- Encourage MFA for all users handling sensitive data
- Provide clear instructions for MFA setup
- Store recovery codes securely

## Compliance

### HIPAA Compliance

- ✅ Access controls (RBAC)
- ✅ Audit logging
- ✅ Data encryption at rest and in transit
- ✅ User authentication
- ✅ Automatic logoff (token expiration)

### GDPR Compliance

- ✅ Right to access (data export)
- ✅ Right to erasure (data deletion)
- ✅ Data anonymization
- ✅ Audit trail
- ✅ Consent management (via permissions)

## Testing

### Test Authentication

```bash
# Register user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Use access token
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test MFA

```bash
# Setup MFA
curl -X POST http://localhost:8001/api/auth/mfa/setup \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Enable MFA (with TOTP token from authenticator app)
curl -X POST http://localhost:8001/api/auth/mfa/enable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'
```

### Test Anonymization

```bash
# Detect PII
curl -X POST http://localhost:8001/api/anonymization/detect-pii \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact me at john@example.com or 555-123-4567"}'

# Anonymize text
curl -X POST http://localhost:8001/api/anonymization/anonymize-text \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact me at john@example.com", "method": "mask"}'
```

## Troubleshooting

### Common Issues

1. **"Could not validate credentials"**
   - Check if token is expired
   - Verify SECRET_KEY is consistent
   - Ensure Authorization header format: `Bearer <token>`

2. **"Permission denied"**
   - Check user roles and permissions
   - Verify RBAC configuration
   - Review audit logs for details

3. **"Invalid MFA token"**
   - Ensure time synchronization on server and client
   - Check if token is within valid window
   - Try using a recovery code

4. **Encryption errors**
   - Verify ENCRYPTION_MASTER_KEY is set
   - Ensure key hasn't changed (data encrypted with old key can't be decrypted with new key)
   - Check for proper base64 encoding

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review audit logs for error details
3. Check application logs for stack traces
4. Refer to the design document for architecture details

## Future Enhancements

- Integration with external identity providers (Google, Microsoft, etc.)
- Hardware security key support (WebAuthn)
- Advanced threat detection
- Automated compliance reporting
- Key management service integration (AWS KMS, HashiCorp Vault)
- Database encryption at rest
- Field-level encryption for specific data types
