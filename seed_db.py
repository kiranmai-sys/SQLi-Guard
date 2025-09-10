from models.db import ensure_tables, get_conn
from config import Config
from datetime import datetime, timedelta

if __name__ == "__main__":
    ensure_tables(Config.DATABASE)
    conn = get_conn(Config.DATABASE)
    cur = conn.cursor()
    
    # Insert sample users
    cur.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
    cur.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('testuser', 'password123', 'user'))
    
    # Insert sample schedules
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    sample_schedules = [
        ('Team Meeting', 'Weekly team sync and project updates', str(today), '09:00', '10:00', 1),
        ('Security Review', 'Monthly security audit and vulnerability assessment', str(tomorrow), '14:00', '16:00', 1),
        ('System Maintenance', 'Scheduled database maintenance and updates', str(next_week), '02:00', '04:00', 1),
        ('Training Session', 'SQL Injection prevention training for developers', str(today + timedelta(days=2)), '10:00', '12:00', 1),
        ('Incident Response Drill', 'Practice security incident response procedures', str(today + timedelta(days=5)), '15:00', '17:00', 1),
    ]
    
    for schedule in sample_schedules:
        cur.execute('''
            INSERT OR IGNORE INTO schedules (title, description, date, start_time, end_time, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', schedule)
    
    conn.commit()
    conn.close()
    print("Seeded database with sample users and schedules.")
    print("\nDemo Credentials:")
    print("Admin: admin / admin123")
    print("User: testuser / password123")