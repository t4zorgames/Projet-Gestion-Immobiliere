from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import ContratLocation


@receiver(post_save, sender=ContratLocation)
def notify_owner_on_contract_created(sender, instance, created, **kwargs):
    if not created:
        return

    bien = getattr(instance, 'bien', None)
    if not bien:
        return

    proprietaire = getattr(bien, 'proprietaire', None)
    user = getattr(proprietaire, 'user', None)

    owner_email = None
    if user and getattr(user, 'email', None):
        owner_email = user.email
    elif proprietaire and getattr(proprietaire, 'email', None):
        owner_email = proprietaire.email

    if not owner_email:
        return

    subject = f"Nouvelle demande de location pour '{bien.titre}'"
    owner_name = user.get_full_name() if user else proprietaire.nom_complet if proprietaire else 'Propriétaire'
    message = (
        f"Bonjour {owner_name},\n\n"
        f"Une nouvelle demande de location a été soumise pour votre bien '{bien.titre}'.\n\n"
        "Détails du locataire :\n"
        f"Nom : {instance.locataire_nom}\n"
        f"Téléphone : {instance.locataire_telephone or 'N/A'}\n"
        f"Email : {instance.locataire_email or 'N/A'}\n"
        f"Infos : {instance.locataire_info or 'N/A'}\n\n"
        "Connectez-vous au tableau de bord pour consulter et gérer la demande.\n"
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner_email], fail_silently=True)
