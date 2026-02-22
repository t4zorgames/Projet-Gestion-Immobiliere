from django.test import TestCase, Client
from django.urls import reverse
from immobilier.models import BienImmobilier, Proprietaire, ContratLocation
from django.contrib.auth.models import User


class TestUserFlow(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_login_and_create_bien(self):
        # Registration
        reg_url = reverse('inscription')
        data = {
            'username': 'tester1',
            'email': 'tester1@example.com',
            'password1': 'StrongPassw0rd!',
            'password2': 'StrongPassw0rd!',
            'is_proprietaire': 'on',
        }
        resp = self.client.post(reg_url, data)
        # should redirect to biens_liste
        self.assertEqual(resp.status_code, 302)

        # user created and logged in
        user = User.objects.filter(username='tester1').first()
        self.assertIsNotNone(user)
        # user should be redirected to login; explicitly login now
        logged = self.client.login(username='tester1', password='StrongPassw0rd!')
        self.assertTrue(logged)
        resp = self.client.get(reverse('biens_liste'))
        self.assertEqual(resp.status_code, 200)

        # Create a Bien (user is not staff)
        create_url = reverse('biens_ajouter')
        bien_data = {
            'titre': 'Appartement Test',
            'adresse': '123 Rue Test',
            'ville': 'yaounde',
            'superficie_m2': '45',
            'loyer_mensuel': '50000.00',
            'type_bien': 'appartement',
            'disponible': 'on',
        }
        resp = self.client.post(create_url, bien_data)
        # creation should redirect to biens_liste
        self.assertEqual(resp.status_code, 302)

        # Verify Bien exists and is linked to the user's Proprietaire
        bien = BienImmobilier.objects.filter(titre='Appartement Test').first()
        self.assertIsNotNone(bien)
        self.assertIsNotNone(bien.proprietaire)
        self.assertEqual(bien.proprietaire.user, user)

    def test_public_access_biens_list_and_detail(self):
        user = User.objects.create_user('owner', 'owner@example.com', 'Password123!')
        proprietaire = Proprietaire.objects.create(user=user, nom_complet='Owner Name', email='owner@example.com')
        bien = BienImmobilier.objects.create(
            titre='Public Apt',
            adresse='Rue Publique 1',
            ville='yaounde',
            superficie_m2=60,
            loyer_mensuel='35000.00',
            type_bien='appartement',
            proprietaire=proprietaire,
            disponible=True,
        )

        # Anonymous should access list and detail
        self.client.logout()
        resp = self.client.get(reverse('biens_liste'))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('biens_detail', args=[bien.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_owner_can_edit_and_delete_bien(self):
        user = User.objects.create_user('owner2', 'o2@example.com', 'Password123!')
        proprietaire = Proprietaire.objects.create(user=user, nom_complet='Owner Two', email='o2@example.com')
        bien = BienImmobilier.objects.create(
            titre='Owner Apt',
            adresse='Rue Owner 2',
            ville='douala',
            superficie_m2=80,
            loyer_mensuel='75000.00',
            type_bien='appartement',
            proprietaire=proprietaire,
            disponible=True,
        )

        # login as owner
        logged = self.client.login(username='owner2', password='Password123!')
        self.assertTrue(logged)

        update_url = reverse('biens_modifier', args=[bien.pk])
        data = {
            'titre': 'Owner Apt Updated',
            'adresse': 'Rue Owner 2',
            'ville': 'douala',
            'superficie_m2': '85',
            'loyer_mensuel': '80000.00',
            'type_bien': 'appartement',
            'disponible': 'on',
        }
        resp = self.client.post(update_url, data)
        self.assertEqual(resp.status_code, 302)
        bien.refresh_from_db()
        self.assertEqual(bien.titre, 'Owner Apt Updated')
        self.assertEqual(bien.superficie_m2, 85)

        delete_url = reverse('biens_supprimer', args=[bien.pk])
        resp = self.client.post(delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(BienImmobilier.objects.filter(pk=bien.pk).exists())

    def test_non_owner_cannot_edit_or_delete_bien(self):
        user = User.objects.create_user('owner3', 'o3@example.com', 'Password123!')
        proprietaire = Proprietaire.objects.create(user=user, nom_complet='Owner Three', email='o3@example.com')
        bien = BienImmobilier.objects.create(
            titre='Owner3 Apt',
            adresse='Rue 3',
            ville='yaounde',
            superficie_m2=70,
            loyer_mensuel='60000.00',
            type_bien='appartement',
            proprietaire=proprietaire,
            disponible=True,
        )

        other = User.objects.create_user('intruder', 'intruder@example.com', 'Password123!')
        self.client.login(username='intruder', password='Password123!')

        update_url = reverse('biens_modifier', args=[bien.pk])
        resp = self.client.post(update_url, {'titre': 'Hacked'})
        self.assertEqual(resp.status_code, 403)

        delete_url = reverse('biens_supprimer', args=[bien.pk])
        resp = self.client.post(delete_url)
        self.assertEqual(resp.status_code, 403)

    def test_contrat_validation_required(self):
        # create owner and a bien that requires contract acceptance
        owner = User.objects.create_user('owner_contract', 'oc@example.com', 'Password123!')
        proprietaire = Proprietaire.objects.create(user=owner, nom_complet='Owner Contract', email='oc@example.com')
        bien = BienImmobilier.objects.create(
            titre='With Contract',
            adresse='Rue Contrat',
            ville='yaounde',
            superficie_m2=50,
            loyer_mensuel='40000.00',
            type_bien='appartement',
            proprietaire=proprietaire,
            disponible=True,
            exige_validation_contrat=True,
        )

        # register a new user and attempt to create a contract without accepting
        resp = self.client.post(reverse('inscription'), {
            'username': 'renter1',
            'email': 'renter1@example.com',
            'password1': 'StrongPassw0rd!',
            'password2': 'StrongPassw0rd!',
        })
        self.assertEqual(resp.status_code, 302)
        # registration redirects to login; login explicitly for the rest of the flow
        logged = self.client.login(username='renter1', password='StrongPassw0rd!')
        self.assertTrue(logged)

        # Try to create a contrat without accepting the owner's contract
        create_url = reverse('contrats_ajouter')
        # pick proprietaire id via query param to populate bien choices
        resp = self.client.post(create_url, {
            'proprietaire': proprietaire.id,
            'bien': bien.id,
            'locataire_nom': 'Renter One',
            'locataire_telephone': '699000000',
            'date_debut': '2026-03-01',
            'date_fin': '2026-04-01',
            'caution': '10000.00',
            # 'accepte_contrat' omitted -> should fail
        })
        # Form should not redirect; it should render with errors (status 200)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ContratLocation.objects.filter(bien=bien, locataire_nom='Renter One').exists())

        # Now accept and submit
        resp = self.client.post(create_url, {
            'proprietaire': proprietaire.id,
            'bien': bien.id,
            'locataire_nom': 'Renter One',
            'locataire_telephone': '699000000',
            'date_debut': '2026-03-01',
            'date_fin': '2026-04-01',
            'caution': '10000.00',
            'accepte_contrat': 'on',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ContratLocation.objects.filter(bien=bien, locataire_nom='Renter One').exists())
