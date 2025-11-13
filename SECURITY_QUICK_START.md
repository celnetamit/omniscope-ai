# Security Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database and create admin user
python scripts/init-security-db.py
```

## Environment Variables

Create a `.env` file:

```bash
# Required
SECRET_KEY=your-secret-key-here
ENCRYPTION_MASTER_KEY=your-encryption-key-here

# Optional (defaults shown)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_EMAIL=admin@omniscope.ai
ADMIN_PASSWORD=admin123
DATABASE_URL=sqlite:///./db/backend.db
```

## Quick Examples

### 1. Register and Login

```python
import requests

# Register
response = requests.post('http://localhost:8001/api/auth/register', json={
    'email': 'user@example.com',
    'password': 'password123',
    'name': 'John Doe'
})

# Login
response = requests.post('http://localhost:8001/api/auth/login', data={
    'username': 'user@example.com',
    'password': 'password123'
})
tokens = response.json()
access_token = tokens['access_token']
```

### 2. Use Protected Endpoints

```python
headers = {'Authorization': f'Bearer {access_token}'}

# Get current user
response = requests.get('http://localhost:8001/api/auth/me', headers=headers)
print(response.json())
```

### 3. Setup MFA

```python
# Setup MFA
response = requests.post('http://localhost:8001/api/auth/mfa/setup', headers=headers)
mfa_data = response.json()

# Save recovery codes securely!
print("Recovery codes:", mfa_data['recovery_codes'])

# Scan QR code with authenticator app
# Then enable MFA with TOTP token
response = requests.post('http://localhost:8001/api/auth/mfa/enable', 
    headers=headers,
    json={'token': '123456'}  # From authenticator app
)
```

### 4. Protect Your Endpoints

```python
from fastapi import APIRouter, Depends
from backend_db.rbac import require_permission, Permissions
from backend_db.auth import get_current_active_user
from backend_db.models import User

router = APIRouter()

# Require authentication only
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.email}"}

# Require specific permission
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_permission(Permissions.SYSTEM_ADMIN))
):
    return {"message": "Admin access granted"}
```

### 5. Anonymize Data

```python
# Detect PII
response = requests.post('http://localhost:8001/api/anonymization/detect-pii',
    headers=headers,
    json={'text': 'Contact me at john@example.com or 555-123-4567'}
)
print(response.json())

# Anonymize text
response = requests.post('http://localhost:8001/api/anonymization/anonymize-text',
    headers=headers,
    json={
        'text': 'Contact me at john@example.com',
        'method': 'mask'
    }
)
print(response.json()['anonymized_text'])
```

### 6. View Audit Logs

```python
# Get your activity
response = requests.get('http://localhost:8001/api/audit/me/activity', headers=headers)
print(response.json())

# Get failed actions (admin only)
response = requests.get('http://localhost:8001/api/audit/logs/failed', headers=headers)
print(response.json())
```

## Default Roles

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| Admin | Full system access | All permissions |
| PI | Principal Investigator | Project management, team management |
| Researcher | Data scientist | Analysis, pipeline creation, model training |
| Analyst | Data analyst | Data viewing, analysis execution |
| Viewer | Read-only | View data and results |

## Common Permissions

```python
from backend_db.rbac import Permissions

# Data
Permissions.DATA_UPLOAD
Permissions.DATA_READ
Permissions.DATA_DELETE

# Pipelines
Permissions.PIPELINE_CREATE
Permissions.PIPELINE_EXECUTE

# Models
Permissions.MODEL_TRAIN
Permissions.MODEL_DEPLOY

# Admin
Permissions.USER_CREATE
Permissions.ROLE_ASSIGN
Permissions.SYSTEM_ADMIN
```

## Assign Roles

```python
# Assign role to user (admin only)
response = requests.post('http://localhost:8001/api/rbac/users/assign-role',
    headers=headers,
    json={
        'user_id': 'user-uuid-here',
        'role_name': 'Researcher'
    }
)
```

## Encryption

```python
from backend_db.encryption import encrypt_data, decrypt_data, hash_data

# Encrypt sensitive data
encrypted = encrypt_data("sensitive information")

# Decrypt
decrypted = decrypt_data(encrypted)

# One-way hash
hashed = hash_data("data to hash")
```

## Troubleshooting

### Token Expired
```python
# Refresh token
response = requests.post('http://localhost:8001/api/auth/refresh',
    json={'refresh_token': refresh_token}
)
new_access_token = response.json()['access_token']
```

### Permission Denied
```python
# Check your permissions
response = requests.get('http://localhost:8001/api/rbac/me/permissions', headers=headers)
print(response.json())
```

### MFA Issues
```python
# Use recovery code instead of TOTP
response = requests.post('http://localhost:8001/api/auth/mfa/verify',
    json={
        'temp_token': temp_token,
        'token': 'RECOVERY-CODE-HERE'
    }
)
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Security Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY and ENCRYPTION_MASTER_KEY
- [ ] Enable HTTPS in production
- [ ] Configure CORS properly
- [ ] Enable MFA for admin accounts
- [ ] Review audit logs regularly
- [ ] Backup encryption keys securely
- [ ] Test GDPR compliance features
- [ ] Set up monitoring and alerts
- [ ] Document security procedures

## Support

For detailed documentation, see:
- `SECURITY_IMPLEMENTATION.md` - Full implementation guide
- `TASK_2_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- API docs at `/docs` - Interactive API documentation
