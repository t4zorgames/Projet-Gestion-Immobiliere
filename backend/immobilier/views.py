from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BienImmobilierForm
from .models import BienImmobilier, ContratLocation, Proprietaire


@login_required
def dashboard(request):
    context = {
        "title": "Accueil / Dashboard",
        "description": "Cette page affichera un résumé global du projet (statistiques principales et accès rapide).",
        "nb_biens": BienImmobilier.objects.count(),
        "nb_proprietaires": Proprietaire.objects.count(),
        "nb_contrats_actifs": ContratLocation.objects.filter(actif=True).count(),
    }
    return render(request, "immobilier/dashboard.html", context)


@login_required
def page_placeholder(request, title, description, pk=None):
    context = {
        "title": title,
        "description": description,
        "pk": pk,
    }
    return render(request, "immobilier/page_placeholder.html", context)


@login_required
def biens_liste(request):
    recherche = request.GET.get("q", "").strip()
    biens = BienImmobilier.objects.select_related("proprietaire").order_by("-cree_le")

    if recherche:
        biens = biens.filter(Q(titre__icontains=recherche) | Q(ville__icontains=recherche))

    context = {
        "title": "Liste des biens",
        "biens": biens,
        "q": recherche,
    }
    return render(request, "immobilier/biens_liste.html", context)


@login_required
def biens_create(request):
    if request.method == "POST":
        form = BienImmobilierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("biens_liste")
    else:
        form = BienImmobilierForm()

    context = {
        "title": "Ajouter un bien",
        "form": form,
    }
    return render(request, "immobilier/biens_form.html", context)


@login_required
def biens_update(request, pk):
    bien = get_object_or_404(BienImmobilier, pk=pk)

    if request.method == "POST":
        form = BienImmobilierForm(request.POST, instance=bien)
        if form.is_valid():
            form.save()
            return redirect("biens_liste")
    else:
        form = BienImmobilierForm(instance=bien)

    context = {
        "title": "Modifier un bien",
        "form": form,
        "bien": bien,
    }
    return render(request, "immobilier/biens_form.html", context)


@login_required
def biens_delete(request, pk):
    bien = get_object_or_404(BienImmobilier, pk=pk)

    if request.method == "POST":
        bien.delete()
        return redirect("biens_liste")

    context = {
        "title": "Supprimer un bien",
        "bien": bien,
    }
    return render(request, "immobilier/biens_confirm_delete.html", context)


@login_required
def biens_detail(request, pk):
    bien = get_object_or_404(BienImmobilier.objects.select_related("proprietaire"), pk=pk)
    context = {
        "title": "Détail d'un bien",
        "bien": bien,
    }
    return render(request, "immobilier/biens_detail.html", context)
