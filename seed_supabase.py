#!/usr/bin/env python3
"""
Supabase Database Seeding Script for SQLi Guard
This script creates demo users and sample schedules in your Supabase database.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_database():
    """Seed the database with demo users and sample schedules."""
    try:
        from models.supabase_db import get_supabase_db
        
        print("🌱 Seeding Supabase database...")
        db = get_supabase_db()
        
        # Create demo users
        print("\n👥 Creating demo users...")
        
        # Admin user
        if not db.user_exists('admin'):
            if db.create_user('admin', 'admin123', 'admin'):
                print("✅ Created admin user: admin/admin123")
            else:
                print("❌ Failed to create admin user")
        else:
            print("ℹ️  Admin user already exists")
        
        # Test user
        if not db.user_exists('testuser'):
            if db.create_user('testuser', 'password123', 'user'):
                print("✅ Created test user: testuser/password123")
            else:
                print("❌ Failed to create test user")
        else:
            print("ℹ️  Test user already exists")
        
        # Create sample schedules
        print("\n📅 Creating sample schedules...")
        
        # Get admin user ID for schedule creation
        admin_user = db.authenticate_user('admin', 'admin123')
        if admin_user:
            admin_id = admin_user['id']
            
            # Sample schedules
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            next_week = today + timedelta(days=7)
            
            sample_schedules = [
                {
                    'title': 'Team Security Meeting',
                    'description': 'Weekly team sync and security updates discussion',
                    'date': str(today),
                    'start_time': '09:00',
                    'end_time': '10:00'
                },
                {
                    'title': 'SQL Injection Training',
                    'description': 'Comprehensive training on SQL injection prevention techniques',
                    'date': str(tomorrow),
                    'start_time': '14:00',
                    'end_time': '16:00'
                },
                {
                    'title': 'Security Audit Review',
                    'description': 'Monthly security audit and vulnerability assessment review',
                    'date': str(next_week),
                    'start_time': '10:00',
                    'end_time': '12:00'
                },
                {
                    'title': 'Incident Response Drill',
                    'description': 'Practice security incident response procedures and protocols',
                    'date': str(today + timedelta(days=3)),
                    'start_time': '15:00',
                    'end_time': '17:00'
                },
                {
                    'title': 'Database Maintenance',
                    'description': 'Scheduled database maintenance and performance optimization',
                    'date': str(today + timedelta(days=5)),
                    'start_time': '02:00',
                    'end_time': '04:00'
                }
            ]
            
            for schedule in sample_schedules:
                if db.create_schedule(
                    schedule['title'],
                    schedule['description'],
                    schedule['date'],
                    schedule['start_time'],
                    schedule['end_time'],
                    admin_id
                ):
                    print(f"✅ Created schedule: {schedule['title']}")
                else:
                    print(f"❌ Failed to create schedule: {schedule['title']}")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n🔐 Demo Credentials:")
        print("   Admin: admin / admin123")
        print("   User:  testuser / password123")
        print("\n🚀 You can now run: python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False

def main():
    """Main function."""
    print("🛡️ SQLi Guard - Database Seeding")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Supabase credentials.")
        print("Copy .env.example to .env and fill in your details.")
        sys.exit(1)
    
    # Seed the database
    if seed_database():
        print("\n✅ Setup complete! Your SQLi Guard is ready to use.")
    else:
        print("\n❌ Setup failed. Please check your Supabase configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()