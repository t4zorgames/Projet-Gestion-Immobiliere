from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.page_placeholder,
        {"title": "Accueil / Dashboard", "description": "Cette page affichera un résumé global du projet (statistiques principales et accès rapide)."},
        name="dashboard",
    ),
    path(
        "connexion/",
        views.page_placeholder,
        {"title": "Connexion", "description": "Cette page contiendra le formulaire de connexion des utilisateurs."},
        name="connexion",
    ),
    path(
        "biens/",
        views.biens_liste,
        name="biens_liste",
    ),
    path(
        "biens/nouveau/",
        views.biens_create,
        name="biens_ajouter",
    ),
    path(
        "biens/<int:pk>/modifier/",
        views.biens_update,
        name="biens_modifier",
    ),
    path(
        "biens/<int:pk>/supprimer/",
        views.biens_delete,
        name="biens_supprimer",
    ),
    path(
        "biens/<int:pk>/",
        views.biens_detail,
        name="biens_detail",
    ),
    path(
        "proprietaires/",
        views.page_placeholder,
        {"title": "Liste des propriétaires", "description": "Cette page affichera les propriétaires enregistrés dans le système."},
        name="proprietaires_liste",
    ),
    path(
        "proprietaires/nouveau/",
        views.page_placeholder,
        {"title": "Ajouter un propriétaire", "description": "Cette page contiendra le formulaire d'ajout d'un propriétaire."},
        name="proprietaires_ajouter",
    ),
    path(
        "proprietaires/<int:pk>/modifier/",
        views.page_placeholder,
        {"title": "Modifier un propriétaire", "description": "Cette page contiendra le formulaire de modification d'un propriétaire."},
        name="proprietaires_modifier",
    ),
    path(
        "proprietaires/<int:pk>/supprimer/",
        views.page_placeholder,
        {"title": "Supprimer un propriétaire", "description": "Cette page demandera la confirmation avant suppression d'un propriétaire."},
        name="proprietaires_supprimer",
    ),
    path(
        "contrats/",
        views.page_placeholder,
        {"title": "Liste des contrats", "description": "Cette page affichera les contrats de location et leur statut (actif/inactif)."},
        name="contrats_liste",
    ),
    path(
        "contrats/nouveau/",
        views.page_placeholder,
        {"title": "Ajouter un contrat", "description": "Cette page contiendra le formulaire d'ajout d'un contrat de location."},
        name="contrats_ajouter",
    ),
    path(
        "contrats/<int:pk>/modifier/",
        views.page_placeholder,
        {"title": "Modifier un contrat", "description": "Cette page contiendra le formulaire de modification d'un contrat de location."},
        name="contrats_modifier",
    ),
    path(
        "contrats/<int:pk>/supprimer/",
        views.page_placeholder,
        {"title": "Supprimer un contrat", "description": "Cette page demandera la confirmation avant suppression d'un contrat de location."},
        name="contrats_supprimer",
    ),
]
