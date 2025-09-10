#!/usr/bin/env python3
"""
Supabase Setup Script for SQLi Guard
This script helps you set up your Supabase project automatically.
"""

import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\n📝 Please create a .env file with your Supabase credentials:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Supabase project details")
        print("\ncp .env.example .env")
        return False
    
    load_dotenv()
    
    required_vars = [
        'VITE_SUPABASE_URL',
        'VITE_SUPABASE_ANON_KEY',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var) or os.environ.get(var).startswith('your-'):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("\n📝 Please update your .env file with actual Supabase credentials")
        return False
    
    return True

def test_connection():
    """Test connection to Supabase."""
    try:
        from models.supabase_db import get_supabase_db
        db = get_supabase_db()
        
        # Test basic connection
        schedules = db.get_all_schedules()
        print(f"✅ Successfully connected to Supabase!")
        print(f"📊 Found {len(schedules)} schedules in database")
        
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def main():
    print("🛡️ SQLi Guard - Supabase Setup")
    print("=" * 40)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print("\n💡 Setup Instructions:")
        print("1. Go to https://supabase.com and create a new project")
        print("2. Go to Settings > API in your Supabase dashboard")
        print("3. Copy your Project URL and API keys to .env file")
        print("4. Run the SQL migrations in the Supabase SQL editor:")
        print("   - supabase/migrations/create_users_table.sql")
        print("   - supabase/migrations/create_schedules_table.sql") 
        print("   - supabase/migrations/create_security_events_table.sql")
        print("5. Run this script again to test the connection")
        sys.exit(1)
    
    print("\n🎉 Setup complete! Your application is ready to use Supabase.")
    print("\n🚀 You can now run: python app.py")

if __name__ == "__main__":
    main()