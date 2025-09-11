#!/usr/bin/env python3
"""
Local Database Setup Script for SQLi Guard
This script sets up a local SQLite database with demo data.
"""

import os
import sys
from datetime import datetime, timedelta
from models.local_db import get_local_db

def setup_database():
    """Set up the local database with demo users and sample schedules."""
    try:
        print("🛡️ SQLi Guard - Local Database Setup")
        print("=" * 50)
        
        # Initialize database
        print("📊 Initializing database...")
        db = get_local_db()
        
        # Create demo users
        print("\n👥 Creating demo users...")
        db.seed_demo_users()
        
        # Create sample schedules
        print("\n📅 Creating sample schedules...")
        db.seed_sample_data()
        
        print("\n🎉 Database setup completed successfully!")
        print("\n🔐 Demo Credentials:")
        print("   Admin: admin / admin123")
        print("   User:  testuser / password123")
        print("\n🚀 You can now run: python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def main():
    """Main function."""
    print("🛡️ SQLi Guard - Local Database Setup")
    print("=" * 50)
    
    # Setup the database
    if setup_database():
        print("\n✅ Setup complete! Your SQLi Guard is ready to use.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()