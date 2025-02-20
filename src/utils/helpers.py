import os
from datetime import datetime

def ensure_directory_exists(path):
    """Ensure that a directory exists, create it if it doesn't."""
    if not os.path.exists(path):
        os.makedirs(path)

def format_datetime(dt):
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")

def get_app_directory():
    """Get the application's data directory."""
    # En Windows: %APPDATA%/CalendarAI
    # En Linux/Mac: ~/.calendar_ai
    if os.name == 'nt':  # Windows
        app_dir = os.path.join(os.getenv('APPDATA'), 'CalendarAI')
    else:  # Linux/Mac
        app_dir = os.path.join(os.path.expanduser("~"), ".calendar_ai")
        
    os.makedirs(app_dir, exist_ok=True)
    return app_dir 