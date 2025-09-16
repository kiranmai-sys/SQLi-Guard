import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class LocalDB:
    def __init__(self, db_path="sqli_guard.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schedules table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Security events table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                username TEXT,
                reason TEXT,
                pattern TEXT,
                snippet TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            hashed_password = self.hash_password(password)
            cur.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # User already exists
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            hashed_password = self.hash_password(password)
            cur.execute(
                'SELECT * FROM users WHERE username = ? AND password = ?',
                (username, hashed_password)
            )
            
            user = cur.fetchone()
            conn.close()
            
            if user:
                return dict(user)
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = cur.fetchone()
            conn.close()
            
            return user is not None
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def seed_demo_users(self) -> bool:
        """Create demo users if they don't exist."""
        try:
            # Create admin user
            if not self.user_exists('admin'):
                if self.create_user('admin', 'admin123', 'admin'):
                    print("✅ Created admin user: admin/admin123")
                else:
                    print("❌ Failed to create admin user")
            
            # Create test user
            if not self.user_exists('testuser'):
                if self.create_user('testuser', 'password123', 'user'):
                    print("✅ Created test user: testuser/password123")
                else:
                    print("❌ Failed to create test user")
            
            return True
        except Exception as e:
            print(f"Error seeding demo users: {e}")
            return False
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules with creator information."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute('''
                SELECT s.*, u.username as created_by_name
                FROM schedules s
                LEFT JOIN users u ON s.created_by = u.id
                ORDER BY s.date ASC, s.start_time ASC
            ''')
            
            schedules = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return schedules
        except Exception as e:
            print(f"Error fetching schedules: {e}")
            return []
    
    def create_schedule(self, title: str, description: str, date: str, start_time: str, end_time: str, created_by: int) -> bool:
        """Create a new schedule."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO schedules (title, description, date, start_time, end_time, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, date, start_time, end_time, created_by))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating schedule: {e}")
            return False
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting schedule: {e}")
            return False
    
    def log_security_event(self, ip: str, username: str, reason: str, pattern: str, snippet: str, user_agent: str) -> bool:
        """Log a security event."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO security_events (ip, username, reason, pattern, snippet, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ip, username, reason, pattern, snippet, user_agent))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging security event: {e}")
            return False
    
    def get_security_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent security events."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute('''
                SELECT * FROM security_events
                ORDER BY ts DESC
                LIMIT ?
            ''', (limit,))
            
            events = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return events
        except Exception as e:
            print(f"Error fetching security events: {e}")
            return []
    
    def get_security_metrics(self) -> List[Dict[str, Any]]:
        """Get security metrics grouped by day."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute('''
                SELECT DATE(ts) as day, COUNT(*) as count
                FROM security_events
                GROUP BY DATE(ts)
                ORDER BY day DESC
                LIMIT 30
            ''')
            
            metrics = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return metrics
        except Exception as e:
            print(f"Error fetching security metrics: {e}")
            return []
    
    def seed_sample_data(self) -> bool:
        """Seed sample schedules."""
        try:
            # Seed fake security events first
            self.seed_fake_security_events()
            
            # Get admin user ID
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            admin_user = cur.fetchone()
            
            if not admin_user:
                conn.close()
                return False
            
            admin_id = admin_user['id']
            
            # Sample schedules
            from datetime import date, timedelta
            today = date.today()
            tomorrow = today + timedelta(days=1)
            next_week = today + timedelta(days=7)
            
            sample_schedules = [
                ('Team Security Meeting', 'Weekly team sync and security updates discussion', str(today), '09:00', '10:00', admin_id),
                ('SQL Injection Training', 'Comprehensive training on SQL injection prevention techniques', str(tomorrow), '14:00', '16:00', admin_id),
                ('Security Audit Review', 'Monthly security audit and vulnerability assessment review', str(next_week), '10:00', '12:00', admin_id),
                ('Incident Response Drill', 'Practice security incident response procedures and protocols', str(today + timedelta(days=3)), '15:00', '17:00', admin_id),
                ('Database Maintenance', 'Scheduled database maintenance and performance optimization', str(today + timedelta(days=5)), '02:00', '04:00', admin_id),
            ]
            
            for schedule in sample_schedules:
                cur.execute('''
                    INSERT OR IGNORE INTO schedules (title, description, date, start_time, end_time, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', schedule)
            
            conn.commit()
            conn.close()
            print("✅ Sample schedules created successfully!")
            return True
        except Exception as e:
            print(f"Error seeding sample data: {e}")
            return False

    def seed_fake_security_events(self) -> bool:
        """Seed fake security events for demonstration."""
        try:
            fake_events = [
                {
                    'ip': '192.168.1.100',
                    'username': 'hacker123',
                    'reason': 'UNION SELECT injection attempt',
                    'pattern': r'(?i)\bunion\b\s+\bselect\b',
                    'snippet': "admin' UNION SELECT username, password FROM users --",
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                {
                    'ip': '10.0.0.50',
                    'username': 'malicious_user',
                    'reason': 'OR condition injection attempt',
                    'pattern': r"(?i)'\s*or\s+\d+\s*=\s*\d+",
                    'snippet': "admin' OR 1=1 --",
                    'user_agent': 'curl/7.68.0'
                },
                {
                    'ip': '172.16.0.25',
                    'username': 'attacker',
                    'reason': 'DROP TABLE injection attempt',
                    'pattern': r'(?i)\bdrop\b\s+\btable\b',
                    'snippet': "admin'; DROP TABLE users; --",
                    'user_agent': 'Python-requests/2.25.1'
                },
                {
                    'ip': '203.0.113.15',
                    'username': 'script_kiddie',
                    'reason': 'Always true condition injection',
                    'pattern': r"(?i)'\s*or\s+'1'\s*=\s*'1",
                    'snippet': "admin' OR '1'='1' --",
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                },
                {
                    'ip': '198.51.100.42',
                    'username': 'anonymous',
                    'reason': 'SLEEP function time-based injection',
                    'pattern': r'(?i)\bsleep\s*\(',
                    'snippet': "admin'; SELECT SLEEP(5); --",
                    'user_agent': 'Wget/1.20.3 (linux-gnu)'
                },
                {
                    'ip': '192.0.2.88',
                    'username': 'bot_scanner',
                    'reason': 'Information schema access attempt',
                    'pattern': r'(?i)\binformation_schema\b',
                    'snippet': "admin' UNION SELECT * FROM information_schema.tables --",
                    'user_agent': 'sqlmap/1.4.7#stable (http://sqlmap.org)'
                },
                {
                    'ip': '203.0.113.99',
                    'username': 'penetration_tester',
                    'reason': 'Database version disclosure attempt',
                    'pattern': r'(?i)@@version|\bversion\s*\(',
                    'snippet': "admin' UNION SELECT @@version --",
                    'user_agent': 'Burp Suite Professional'
                },
                {
                    'ip': '10.0.0.123',
                    'username': 'red_team',
                    'reason': 'WAITFOR DELAY time-based injection',
                    'pattern': r'(?i)\bwaitfor\s+delay\b',
                    'snippet': "admin'; WAITFOR DELAY '00:00:05' --",
                    'user_agent': 'Mozilla/5.0 (compatible; Nmap Scripting Engine)'
                },
                {
                    'ip': '172.16.0.77',
                    'username': 'automated_scanner',
                    'reason': 'Hexadecimal encoding injection',
                    'pattern': r'(?i)0x[0-9a-fA-F]+',
                    'snippet': "admin' AND 1=0x41424344 --",
                    'user_agent': 'Nikto/2.1.6'
                },
                {
                    'ip': '198.51.100.200',
                    'username': 'threat_actor',
                    'reason': 'Comment injection attempt',
                    'pattern': r'(?i)--|#|/\*',
                    'snippet': "admin'/* malicious comment */--",
                    'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0)'
                }
            ]
            
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Check if fake events already exist
            cur.execute('SELECT COUNT(*) FROM security_events WHERE ip = ?', ('192.168.1.100',))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True  # Already seeded
            
            # Insert fake security events with timestamps spread over the last few days
            from datetime import datetime, timedelta
            import random
            
            for i, event in enumerate(fake_events):
                # Create timestamps spread over the last 7 days
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                cur.execute('''
                    INSERT INTO security_events (ts, ip, username, reason, pattern, snippet, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp.isoformat(),
                    event['ip'],
                    event['username'],
                    event['reason'],
                    event['pattern'],
                    event['snippet'],
                    event['user_agent']
                ))
            
            conn.commit()
            conn.close()
            print("✅ Fake security events created successfully!")
            return True
        except Exception as e:
            print(f"Error seeding fake security events: {e}")
            return False
    
    def seed_fake_users(self) -> bool:
        """Create additional fake users for demonstration."""
        try:
            fake_users = [
                ('john_doe', 'password123', 'user'),
                ('jane_smith', 'securepass456', 'user'),
                ('bob_wilson', 'mypassword789', 'user'),
                ('alice_johnson', 'strongpass321', 'user'),
                ('charlie_brown', 'userpass654', 'user'),
                ('diana_prince', 'wonderpass987', 'user'),
                ('peter_parker', 'spideypass123', 'user'),
                ('mary_jane', 'mjpass456', 'user'),
                ('bruce_wayne', 'batmanpass789', 'user'),
                ('clark_kent', 'supermanpass321', 'user'),
                ('security_admin', 'secadmin123', 'admin'),
                ('system_monitor', 'monitor456', 'admin')
            ]
            
            for username, password, role in fake_users:
                if not self.user_exists(username):
                    self.create_user(username, password, role)
            
            print("✅ Fake users created successfully!")
            return True
        except Exception as e:
            print(f"Error seeding fake users: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin management."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute('''
                SELECT id, username, role, created_at
                FROM users
                ORDER BY created_at DESC
            ''')
            
            users = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID (except admin users)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Check if user is admin
            cur.execute('SELECT role FROM users WHERE id = ?', (user_id,))
            user = cur.fetchone()
            
            if not user:
                conn.close()
                return False
            
            # Don't allow deletion of admin users
            if user[0] == 'admin':
                conn.close()
                return False
            
            cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
# Global instance
local_db = None

def get_local_db():
    """Get or create local database instance."""
    global local_db
    if local_db is None:
        local_db = LocalDB()
    return local_db