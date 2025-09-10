import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE = os.environ.get("DATABASE_URL", os.path.join(os.path.dirname(__file__), "users.db"))
    LOG_DB = os.environ.get("LOG_DB_URL", os.path.join(os.path.dirname(__file__), "security.db"))
    LOG_FILE = os.environ.get("LOG_FILE", os.path.join(os.path.dirname(__file__), "logs", "security.log"))
    RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", 20))  # requests
    RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))      # seconds
    IP_BLOCKLIST = set(ip.strip() for ip in os.environ.get("IP_BLOCKLIST", "").split(",") if ip.strip())
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "adminpanel")
