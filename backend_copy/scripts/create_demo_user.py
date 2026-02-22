import os
import sys
import django

# ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

username = 'demo'
password = 'DemoPass123!'
email = 'demo@example.com'

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.email = email
user.is_active = True
user.save()

if created:
    print(f'Created demo user: {username} / {password} ({email})')
else:
    print(f'Updated existing user password and marked active: {username} / {password} ({email})')
print('You can now log in at http://127.0.0.1:8001/connexion/')
