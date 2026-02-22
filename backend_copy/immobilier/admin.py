from django.contrib import admin
from .models import BienImmobilier, ContratLocation, Proprietaire


@admin.register(Proprietaire)
class ProprietaireAdmin(admin.ModelAdmin):
    list_display = ("nom_complet", "email", "telephone", "user")
    search_fields = ("nom_complet", "email", "telephone", "user__username")


@admin.register(BienImmobilier)
class BienImmobilierAdmin(admin.ModelAdmin):
    list_display = ("titre", "type_bien", "ville", "loyer_mensuel", "disponible", "proprietaire")
    list_filter = ("type_bien", "ville", "disponible")
    search_fields = ("titre", "adresse", "ville")
    # no contract preview: contracts are generated from owner/property data


@admin.register(ContratLocation)
class ContratLocationAdmin(admin.ModelAdmin):
    list_display = ("bien", "locataire_nom", "date_debut", "date_fin", "actif")
    list_filter = ("actif", "date_debut", "date_fin")
    search_fields = ("locataire_nom", "bien__titre")
