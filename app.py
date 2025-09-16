from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify, session, flash
from detectors.sqli import is_malicious
from models.local_db import get_local_db
from utils.rate_limiter import SimpleRateLimiter
from config import Config
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Local Database connection
try:
    db = get_local_db()
    # Seed demo users on startup
    db.seed_demo_users()
    # Seed fake users for demonstration
    db.seed_fake_users()
    # Seed sample data
    db.seed_sample_data()
    print("✅ Successfully connected to Local Database!")
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")
    exit(1)

rate_limiter = SimpleRateLimiter(limit=app.config['RATE_LIMIT_REQUESTS'], window=app.config['RATE_LIMIT_WINDOW'])

@app.after_request
def set_security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
    return resp

@app.before_request
def check_ip_blocklist_and_rate():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip in app.config['IP_BLOCKLIST']:
        return render_template('blocked.html', reason="IP blocklist"), 403
    key = f"{ip}:{request.path}"
    if not rate_limiter.allow(key):
        return render_template('blocked.html', reason="Rate limit exceeded"), 429

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # SQLi detection on raw inputs
    hit = is_malicious(username, password)
    if hit:
        db.log_security_event(
            request.headers.get('X-Forwarded-For', request.remote_addr),
            username,
            hit['description'],
            hit['pattern'],
            hit['snippet'],
            request.headers.get('User-Agent', '')
        )
        resp = make_response(render_template('blocked.html', reason="SQL Injection detected"))
        resp.status_code = 403
        return resp

    # Authenticate user with Local Database
    user = db.authenticate_user(username, password)

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        flash(f"Welcome back, {user['username']}!", "success")
        
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_schedule'))
    else:
        flash("Invalid credentials. Please try again.", "error")
        return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f"Goodbye, {username}! You have been logged out successfully.", "success")
    return redirect(url_for('index'))

@app.route('/user/schedule')
def user_schedule():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('index'))
    
    schedules = db.get_all_schedules()
    
    return render_template('user_schedule.html', schedules=schedules)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('index'))
    
    # Get security events and schedules from Local Database
    security_events = db.get_security_events()
    schedules = db.get_all_schedules()
    users = db.get_all_users()
    
    return render_template('admin_dashboard.html', security_events=security_events, schedules=schedules, users=users)

@app.route('/admin/schedule/add', methods=['GET', 'POST'])
def add_schedule():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        date = request.form.get('date', '')
        start_time = request.form.get('start_time', '')
        end_time = request.form.get('end_time', '')
        
        # SQLi detection on inputs
        hit = is_malicious(title, description)
        if hit:
            db.log_security_event(
                request.headers.get('X-Forwarded-For', request.remote_addr),
                session.get('username', ''),
                hit['description'],
                hit['pattern'],
                hit['snippet'],
                request.headers.get('User-Agent', '')
            )
            flash("Invalid input detected. Please check your data.", "error")
            return render_template('add_schedule.html')
        
        # Create schedule in Local Database
        success = db.create_schedule(title, description, date, start_time, end_time, session['user_id'])
        
        if success:
            flash("Schedule added successfully!", "success")
        else:
            flash("Error adding schedule. Please try again.", "error")
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_schedule.html')

@app.route('/admin/schedule/delete/<int:schedule_id>')
def delete_schedule(schedule_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('index'))
    
    success = db.delete_schedule(schedule_id)
    
    if success:
        flash("Schedule deleted successfully!", "success")
    else:
        flash("Error deleting schedule. Please try again.", "error")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/delete/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('index'))
    
    success = db.delete_user(user_id)
    
    if success:
        flash("User deleted successfully!", "success")
    else:
        flash("Error deleting user. Admin users cannot be deleted.", "error")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    metrics = db.get_security_metrics()
    return jsonify(metrics)

if __name__ == '__main__':
    print("🛡️ SQLi Guard - Starting Application")
    print("=" * 50)
    print("✅ Local SQLite Database Ready")
    print("🔐 Demo Credentials:")
    print("   Admin: admin / admin123")
    print("   User:  testuser / password123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)