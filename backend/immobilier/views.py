from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BienImmobilier, Proprietaire, ContratLocation


@login_required
def dashboard(request):
    context = {
        "nb_biens": BienImmobilier.objects.count(),
        "nb_proprietaires": Proprietaire.objects.count(),
        "nb_contrats_actifs": ContratLocation.objects.filter(actif=True).count(),
        "nb_biens_disponibles": BienImmobilier.objects.filter(disponible=True).count(),
    }
    return render(request, "immobilier/Dashboard.html", context)


def page_placeholder(request, title, description, pk=None):
    context = {
        "title": title,
        "description": description,
        "pk": pk,
    }
    return render(request, "immobilier/page_placeholder.html", context)