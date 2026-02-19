from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="connexion",
    ),
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(),
        name="deconnexion",
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
