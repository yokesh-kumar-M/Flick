import os
import sys
from pathlib import Path

# Add the gateway directory and root directory to python path for Vercel
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent)) # Root (Flick/)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_project.settings')
application = get_wsgi_application()

# Vercel expects the application to be named 'app'
app = application
