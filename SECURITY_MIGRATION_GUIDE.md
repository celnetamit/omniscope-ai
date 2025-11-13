# Security Migration Guide

## Overview

This guide helps you migrate your existing OmniScope AI installation to include the new authentication and security features.

## Pre-Migration Checklist

- [ ] Backup your existing database
- [ ] Review current user access patterns
- [ ] Plan role assignments for existing users
- [ ] Prepare communication for users about new authentication
- [ ] Test migration in a development environment first

## Migration Steps

### Step 1: Backup Existing Data

```bash
# Backup SQLite database
cp db/backend.db db/backend.db.backup

# Backup custom database if exists
cp db/custom.db db/custom.db.backup
```

### Step 2: Install New Dependencies

```bash
# Update dependencies
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

Create or update `.env` file:

```bash
# Generate keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_MASTER_KEY=' + Fernet.generate_key().decode())"

# Add to .env
SECRET_KEY=<generated-key>
ENCRYPTION_MASTER_KEY=<generated-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Step 4: Initialize Security Database

```bash
# Run initialization script
python scripts/init-security-db.py
```

This will:
- Create new security tables
- Create default roles (Admin, PI, Researcher, Analyst, Viewer)
- Create admin user

### Step 5: Migrate Existing Users (If Any)

If you have existing users in your system, you'll need to migrate them:

```python
# migration_script.py
from backend_db.database import SessionLocal
from backend_db.models import User
from backend_db.auth import AuthService
from backend_db.rbac import RBACService

db = SessionLocal()

# Example: Create users from existing data
existing_users = [
    {'email': 'user1@example.com', 'name': 'User 1', 'role': 'Researcher'},
    {'email': 'user2@example.com', 'name': 'User 2', 'role': 'Analyst'},
]

for user_data in existing_users:
    # Check if user exists
    existing = AuthService.get_user_by_email(db, user_data['email'])
    if not existing:
        # Create user with temporary password
        temp_password = 'ChangeMe123!'
        user = User(
            email=user_data['email'],
            password_hash=AuthService.get_password_hash(temp_password),
            name=user_data['name'],
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign role
        RBACService.assign_role_to_user(db, user, user_data['role'])
        
        print(f"Created user: {user_data['email']} with role {user_data['role']}")
        print(f"Temporary password: {temp_password}")

db.close()
```

### Step 6: Update Frontend Authentication

Update your frontend to use the new authentication endpoints:

```typescript
// Before (no auth)
const response = await fetch('/api/data/upload', {
    method: 'POST',
    body: formData
});

// After (with auth)
const token = localStorage.getItem('access_token');
const response = await fetch('/api/data/upload', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: formData
});
```

### Step 7: Add Login Flow to Frontend

```typescript
// Login component
async function login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return true;
    }
    return false;
}

// Token refresh
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        return true;
    }
    return false;
}

// Logout
async function logout() {
    const token = localStorage.getItem('access_token');
    await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}
```

### Step 8: Update Existing API Endpoints

Add authentication to your existing endpoints:

```python
# Before
@router.post("/upload")
async def upload_file(file: UploadFile):
    # Process file
    pass

# After
from backend_db.auth import get_current_active_user
from backend_db.rbac import require_permission, Permissions

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(require_permission(Permissions.DATA_UPLOAD))
):
    # Process file
    # Now you have access to current_user
    pass
```

### Step 9: Test Migration

1. **Test Authentication:**
   ```bash
   # Login as admin
   curl -X POST http://localhost:8001/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@omniscope.ai&password=admin123"
   ```

2. **Test Protected Endpoints:**
   ```bash
   # Use token from login
   curl -X GET http://localhost:8001/api/auth/me \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Test Role Permissions:**
   ```bash
   # Check permissions
   curl -X GET http://localhost:8001/api/rbac/me/permissions \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Step 10: User Communication

Send email to existing users:

```
Subject: Important: New Authentication System

Dear OmniScope AI User,

We've upgraded our security system to better protect your data. Here's what you need to know:

1. New Login Required
   - You'll need to log in with your email and a temporary password
   - Temporary password: [TEMP_PASSWORD]
   - Please change this immediately after first login

2. Multi-Factor Authentication (Optional but Recommended)
   - We now support MFA for enhanced security
   - Set it up in your profile settings

3. New Features
   - Role-based access control
   - Audit logging of all actions
   - Data anonymization tools
   - GDPR compliance features

4. What to Do Now
   - Log in at: http://your-omniscope-url.com
   - Change your password
   - Set up MFA (recommended)
   - Review your permissions

If you have any questions, please contact support.

Best regards,
OmniScope AI Team
```

## Post-Migration Tasks

### 1. Verify All Users Can Login

```python
# Check all users
from backend_db.database import SessionLocal
from backend_db.models import User

db = SessionLocal()
users = db.query(User).all()

for user in users:
    print(f"User: {user.email}")
    print(f"  Active: {user.is_active}")
    print(f"  Roles: {[role.name for role in user.roles]}")
    print(f"  MFA: {user.mfa_enabled}")
    print()

db.close()
```

### 2. Assign Appropriate Roles

Review and assign roles based on user responsibilities:

```python
# Assign roles
from backend_db.database import SessionLocal
from backend_db.rbac import RBACService
from backend_db.auth import AuthService

db = SessionLocal()

# Example role assignments
role_assignments = {
    'pi@lab.edu': 'PI',
    'researcher1@lab.edu': 'Researcher',
    'analyst1@lab.edu': 'Analyst',
    'viewer1@lab.edu': 'Viewer'
}

for email, role_name in role_assignments.items():
    user = AuthService.get_user_by_email(db, email)
    if user:
        RBACService.assign_role_to_user(db, user, role_name)
        print(f"Assigned {role_name} to {email}")

db.close()
```

### 3. Enable Audit Logging

Audit logging is automatically enabled. Review logs:

```bash
# View recent activity
curl -X GET "http://localhost:8001/api/audit/logs?limit=50" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 4. Configure Monitoring

Set up monitoring for:
- Failed login attempts
- Permission denied errors
- Unusual activity patterns
- Token expiration issues

### 5. Update Documentation

Update your internal documentation to include:
- New login procedures
- Role descriptions
- Permission matrix
- MFA setup instructions
- Password reset procedures

## Rollback Plan

If you need to rollback:

```bash
# Stop the application
# Restore database backup
cp db/backend.db.backup db/backend.db

# Revert code changes
git checkout <previous-commit>

# Restart application
python main.py
```

## Common Migration Issues

### Issue 1: Users Can't Login

**Solution:**
- Verify user exists in database
- Check password hash is correct
- Ensure user is active (`is_active=True`)
- Check for typos in email

### Issue 2: Permission Denied Errors

**Solution:**
- Verify user has appropriate role
- Check role has required permissions
- Review audit logs for details

### Issue 3: Token Expiration

**Solution:**
- Implement token refresh in frontend
- Adjust token expiration times if needed
- Handle 401 errors gracefully

### Issue 4: MFA Issues

**Solution:**
- Verify time synchronization
- Use recovery codes if TOTP fails
- Regenerate MFA secret if needed

## Gradual Migration Strategy

For large deployments, consider gradual migration:

### Phase 1: Parallel Systems (Week 1-2)
- Run new auth system alongside old system
- Allow users to opt-in to new system
- Monitor for issues

### Phase 2: Encourage Migration (Week 3-4)
- Send reminders to migrate
- Offer support for migration
- Identify and resolve issues

### Phase 3: Mandatory Migration (Week 5)
- Set deadline for migration
- Disable old authentication
- Provide emergency support

### Phase 4: Cleanup (Week 6+)
- Remove old authentication code
- Archive old user data
- Document lessons learned

## Security Hardening Post-Migration

1. **Change Default Admin Password**
   ```bash
   curl -X POST http://localhost:8001/api/auth/change-password \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"old_password": "admin123", "new_password": "NewSecurePassword123!"}'
   ```

2. **Enable MFA for Admins**
   - Require all admin accounts to enable MFA
   - Set up monitoring for admin actions

3. **Review Permissions**
   - Audit all role assignments
   - Apply principle of least privilege
   - Remove unnecessary permissions

4. **Configure Rate Limiting**
   - Add rate limiting to login endpoint
   - Implement account lockout after failed attempts

5. **Set Up Alerts**
   - Failed login attempts
   - Permission changes
   - Data exports
   - Admin actions

## Support

For migration support:
1. Review `SECURITY_IMPLEMENTATION.md` for detailed documentation
2. Check API docs at `/docs`
3. Review audit logs for issues
4. Contact your system administrator

## Checklist

- [ ] Backup completed
- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] Security database initialized
- [ ] Existing users migrated
- [ ] Frontend updated
- [ ] API endpoints protected
- [ ] Migration tested
- [ ] Users notified
- [ ] Roles assigned
- [ ] Audit logging verified
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Admin password changed
- [ ] MFA enabled for admins
- [ ] Rollback plan documented
