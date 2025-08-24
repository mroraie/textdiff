import os
import sys

sys.path.insert(0, '/home/errczdis/textdiff')  # ← Update path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textdiff.settings')  # ← Project name

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()