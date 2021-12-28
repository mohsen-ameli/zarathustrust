import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, '/home/pi/money_moe/users')
sys.path.insert(0, '/home/pi/money_moe/accounts/') 
sys.path.insert(0, '/home/pi/money_moe/money_moe/')
sys.path.append('/home/pi/money_moe/venv/bin/python3')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'money_moe.settings')
os.environ['HTTPS'] = "on"
os.environ['wsgi.url_scheme'] = 'https'

application = get_wsgi_application()
