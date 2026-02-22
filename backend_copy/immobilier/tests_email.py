from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from datetime import date

from .models import Proprietaire, BienImmobilier, ContratLocation


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailNotificationTest(TestCase):
    def test_email_sent_on_contrat_creation(self):
        user = User.objects.create(username='owner_test', email='owner@test.local')
        p = Proprietaire.objects.create(user=user, nom_complet='Owner Test', email='owner@test.local')

        b = BienImmobilier.objects.create(
            titre='Test Bien',
            adresse='Rue Test',
            ville='yaounde',
            superficie_m2=30,
            loyer_mensuel='200.00',
            type_bien='appartement',
            proprietaire=p,
            exige_validation_contrat=True,
        )

        # Ensure outbox is empty
        mail.outbox.clear()

        ContratLocation.objects.create(
            bien=b,
            locataire_nom='Test Loc',
            locataire_telephone='000',
            locataire_email='loc@test.local',
            locataire_info='Info',
            date_debut=date(2026, 3, 1),
            date_fin=date(2026, 3, 10),
            caution='100.00',
        )

        # The signal should have sent an email
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn("Nouvelle demande de location", sent.subject)
        self.assertIn('Test Loc', sent.body)