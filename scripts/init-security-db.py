#!/usr/bin/env python3
"""
Initialize security database tables and default data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_db.database import init_database, SessionLocal
from backend_db.rbac import RBACService
from backend_db.auth import AuthService
from backend_db.models import User

def main():
    print("🔐 Initializing security database...")
    
    # Initialize database
    init_database()
    print("✅ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create default roles
        RBACService.create_default_roles(db)
        print("✅ Default roles created")
        
        # Create admin user if it doesn't exist
        admin_email = os.getenv("ADMIN_EMAIL", "admin@omniscope.ai")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # Change in production!
        
        existing_admin = AuthService.get_user_by_email(db, admin_email)
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=AuthService.get_password_hash(admin_password),
                name="System Administrator",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Assign Admin role
            RBACService.assign_role_to_user(db, admin_user, "Admin")
            
            print(f"✅ Admin user created: {admin_email}")
            print(f"⚠️  Default password: {admin_password}")
            print("⚠️  CHANGE THIS PASSWORD IMMEDIATELY IN PRODUCTION!")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
        
        print("\n🎉 Security database initialization complete!")
        print("\nDefault Roles:")
        print("  - Admin: Full system access")
        print("  - PI: Principal Investigator - project management")
        print("  - Researcher: Can perform analysis and create pipelines")
        print("  - Analyst: Can view and analyze data")
        print("  - Viewer: Read-only access")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
