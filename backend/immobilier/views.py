from django.shortcuts import render
from .models import BienImmobilier, ContratLocation, Proprietaire


def home(request):
	context = {
		"nb_proprietaires": Proprietaire.objects.count(),
		"nb_biens": BienImmobilier.objects.count(),
		"nb_contrats_actifs": ContratLocation.objects.filter(actif=True).count(),
	}
	return render(request, "immobilier/home.html", context)
