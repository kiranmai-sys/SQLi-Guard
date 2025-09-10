import os
import asyncio
import hashlib
from supabase import create_client, Client
from typing import Optional, List, Dict, Any

class SupabaseDB:
    def __init__(self):
        self.url = os.environ.get("VITE_SUPABASE_URL")
        self.key = os.environ.get("VITE_SUPABASE_ANON_KEY")
        self.service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.url, self.key, self.service_key]):
            raise ValueError("Missing Supabase environment variables. Please check your .env file.")
        
        # Client for authenticated operations
        self.supabase: Client = create_client(self.url, self.key)
        # Admin client for service operations
        self.admin_client: Client = create_client(self.url, self.service_key)
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing for demo purposes."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create a new user."""
        try:
            hashed_password = self.hash_password(password)
            response = self.admin_client.table('users').insert({
                'username': username,
                'password': hashed_password,
                'role': role
            }).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            hashed_password = self.hash_password(password)
            response = self.supabase.table('users').select('*').eq('username', username).eq('password', hashed_password).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        try:
            response = self.supabase.table('users').select('id').eq('username', username).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def seed_demo_users(self) -> bool:
        """Create demo users if they don't exist."""
        try:
            # Create admin user
            if not self.user_exists('admin'):
                self.create_user('admin', 'admin123', 'admin')
                print("✅ Created admin user: admin/admin123")
            
            # Create test user
            if not self.user_exists('testuser'):
                self.create_user('testuser', 'password123', 'user')
                print("✅ Created test user: testuser/password123")
            
            return True
        except Exception as e:
            print(f"Error seeding demo users: {e}")
            return False
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules with creator information."""
        try:
            response = self.supabase.table('schedules').select('''
                *,
                users!schedules_created_by_fkey(username)
            ''').order('date', desc=False).order('start_time', desc=False).execute()
            
            # Flatten the user data
            schedules = []
            for schedule in response.data:
                schedule_data = dict(schedule)
                if schedule_data.get('users'):
                    schedule_data['created_by_name'] = schedule_data['users']['username']
                else:
                    schedule_data['created_by_name'] = 'Unknown'
                del schedule_data['users']
                schedules.append(schedule_data)
            
            return schedules
        except Exception as e:
            print(f"Error fetching schedules: {e}")
            return []
    
    def create_schedule(self, title: str, description: str, date: str, start_time: str, end_time: str, created_by: str) -> bool:
        """Create a new schedule."""
        try:
            response = self.supabase.table('schedules').insert({
                'title': title,
                'description': description,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'created_by': created_by
            }).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error creating schedule: {e}")
            return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule by ID."""
        try:
            response = self.supabase.table('schedules').delete().eq('id', schedule_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting schedule: {e}")
            return False
    
    def log_security_event(self, ip: str, username: str, reason: str, pattern: str, snippet: str, user_agent: str) -> bool:
        """Log a security event."""
        try:
            response = self.admin_client.table('security_events').insert({
                'ip': ip,
                'username': username,
                'reason': reason,
                'pattern': pattern,
                'snippet': snippet,
                'user_agent': user_agent
            }).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error logging security event: {e}")
            return False
    
    def get_security_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent security events."""
        try:
            response = self.admin_client.table('security_events').select('*').order('ts', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching security events: {e}")
            return []
    
    def get_security_metrics(self) -> List[Dict[str, Any]]:
        """Get security metrics grouped by day."""
        try:
            # Note: This is a simplified version. For complex aggregations,
            # you might want to use Supabase Edge Functions or PostgreSQL functions
            response = self.admin_client.table('security_events').select('ts').execute()
            
            # Group by day in Python (in production, use SQL aggregation)
            from collections import defaultdict
            from datetime import datetime
            
            daily_counts = defaultdict(int)
            for event in response.data:
                date_str = event['ts'][:10]  # Extract YYYY-MM-DD
                daily_counts[date_str] += 1
            
            return [{'day': day, 'count': count} for day, count in sorted(daily_counts.items())]
        except Exception as e:
            print(f"Error fetching security metrics: {e}")
            return []

# Global instance
supabase_db = None

def get_supabase_db():
    """Get or create Supabase database instance."""
    global supabase_db
    if supabase_db is None:
        supabase_db = SupabaseDB()
    return supabase_db