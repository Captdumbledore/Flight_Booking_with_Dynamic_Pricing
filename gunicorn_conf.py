"""Gunicorn configuration for Render deployment"""

import os

# Gunicorn config
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
worker_connections = 1000

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Server Mechanics
preload_app = True
worker_tmp_dir = "/dev/shm"  # Use memory for temporary files
forwarded_allow_ips = "*"