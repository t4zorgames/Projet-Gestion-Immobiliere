from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="connexion",
    ),
    path("inscription/", views.register, name="inscription"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="deconnexion"),

    path("biens/", views.biens_liste, name="biens_liste"),
    path("biens/nouveau/", views.biens_create, name="biens_ajouter"),
    path("biens/<int:pk>/modifier/", views.biens_update, name="biens_modifier"),
    path("biens/<int:pk>/supprimer/", views.biens_delete, name="biens_supprimer"),
    path("biens/<int:pk>/", views.biens_detail, name="biens_detail"),

    path("proprietaires/", views.proprietaires_liste, name="proprietaires_liste"),
    path("proprietaires/nouveau/", views.proprietaires_create, name="proprietaires_ajouter"),
    path("proprietaires/<int:pk>/modifier/", views.proprietaires_update, name="proprietaires_modifier"),
    path("proprietaires/<int:pk>/supprimer/", views.proprietaires_delete, name="proprietaires_supprimer"),

    path("contrats/", views.contrats_liste, name="contrats_liste"),
    path("contrats/nouveau/", views.contrats_create, name="contrats_ajouter"),
    path("contrats/<int:pk>/modifier/", views.contrats_update, name="contrats_modifier"),
    path("contrats/<int:pk>/supprimer/", views.contrats_delete, name="contrats_supprimer"),
    path("proprietaire/demandes/", views.proprietaire_demandes, name="proprietaire_demandes"),
    path("devenir-proprietaire/", views.devenir_proprietaire, name="devenir_proprietaire"),
]
