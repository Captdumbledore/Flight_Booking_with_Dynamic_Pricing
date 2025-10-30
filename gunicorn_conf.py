"""Gunicorn configuration for Render deployment"""

workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:10000"  # Using Render's required port
accesslog = "-"
errorlog = "-"