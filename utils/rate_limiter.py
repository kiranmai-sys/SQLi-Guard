import time
from collections import defaultdict

class SimpleRateLimiter:
    def __init__(self, limit=20, window=60):
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)
    
    def allow(self, key):
        """Check if request is allowed for the given key."""
        now = time.time()
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < self.window]
        
        if len(self.requests[key]) >= self.limit:
            return False
        
        self.requests[key].append(now)
        return True