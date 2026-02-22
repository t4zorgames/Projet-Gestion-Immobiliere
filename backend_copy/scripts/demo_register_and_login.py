import os
import sys
import django

# ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

c = Client()

username = 'demo_user'
password = 'DemoPass123!'
email = 'demo_user@example.com'

print('--- Registration request ---')
reg_url = reverse('inscription')
resp = c.post(reg_url, {
    'username': username,
    'email': email,
    'password1': password,
    'password2': password,
    # normal user: do not set is_proprietaire
}, HTTP_HOST='127.0.0.1')
print('Registration POST status:', resp.status_code)
if resp.status_code in (301,302):
    print('Redirected to:', resp['Location'])

# Check login page
print('\n--- Retrieve login page ---')
login_url = reverse('connexion')
resp = c.get(login_url, HTTP_HOST='127.0.0.1')
print('Login GET status:', resp.status_code)
print('Login page contains success message?' , ('Compte créé' in resp.content.decode('utf-8')))

# Now attempt login
print('\n--- Login attempt ---')
resp = c.post(login_url, {'username': username, 'password': password}, HTTP_HOST='127.0.0.1')
print('Login POST status:', resp.status_code)
# After login should redirect
if resp.status_code in (301,302):
    print('Login redirected to:', resp['Location'])

# Access dashboard to verify authenticated
from django.urls import reverse
resp = c.get(reverse('dashboard'), HTTP_HOST='127.0.0.1')
print('\n--- Access dashboard ---')
print('Dashboard GET status:', resp.status_code)
print('Dashboard content snippet:')
print(resp.content.decode('utf-8')[:400])

# cleanup: remove created user if exists
try:
    u = User.objects.filter(username=username).first()
    if u:
        u.delete()
        print('\nCreated demo user deleted.')
except Exception as e:
    print('Cleanup error:', e)
