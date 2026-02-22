import os
import sys
import django

# Ensure project root is on sys.path so `config` module is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from immobilier.models import Proprietaire, BienImmobilier, ContratLocation
from datetime import date

u, created = User.objects.get_or_create(
    username='owner_demo',
    defaults={'email': 'owner@example.com', 'first_name': 'Owner', 'last_name': 'Demo'}
)
if created:
    u.set_password('pass')
    u.save()

p, _ = Proprietaire.objects.get_or_create(
    user=u,
    defaults={'nom_complet': 'Owner Demo', 'email': 'owner@example.com', 'telephone': '000'}
)

b, _ = BienImmobilier.objects.get_or_create(
    titre='Demo Bien',
    defaults={
        'adresse': 'Rue Demo',
        'ville': 'yaounde',
        'superficie_m2': 50,
        'loyer_mensuel': '100.00',
        'type_bien': 'maison',
        'proprietaire': p,
        'exige_validation_contrat': True,
    }
)

c = ContratLocation.objects.create(
    bien=b,
    locataire_nom='Loc Demo',
    locataire_telephone='111',
    locataire_email='loc@example.com',
    locataire_info='Demonstration request',
    date_debut=date(2026, 3, 1),
    date_fin=date(2026, 3, 10),
    caution='50.00'
)

print('Created contract:', c)
print('If EMAIL_BACKEND is console, the email content should have been printed above.')
