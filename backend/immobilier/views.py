from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .forms import BienImmobilierForm, ContratLocationForm, ProprietaireForm
from .models import BienImmobilier, ContratLocation, Proprietaire


@login_required
def dashboard(request):
    context = {
        "nb_biens": BienImmobilier.objects.count(),
        "nb_proprietaires": Proprietaire.objects.count(),
        "nb_contrats_actifs": ContratLocation.objects.filter(actif=True).count(),
        "nb_biens_disponibles": BienImmobilier.objects.filter(disponible=True).count(),
    }
    return render(request, "immobilier/Dashboard.html", context)


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
    context = {"title": "Liste des biens", "biens": biens, "q": recherche}
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
    context = {"title": "Ajouter un bien", "form": form}
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
    context = {"title": "Modifier un bien", "form": form, "bien": bien}
    return render(request, "immobilier/biens_form.html", context)


@login_required
def biens_delete(request, pk):
    bien = get_object_or_404(BienImmobilier, pk=pk)
    if request.method == "POST":
        bien.delete()
        return redirect("biens_liste")
    context = {"title": "Supprimer un bien", "bien": bien}
    return render(request, "immobilier/biens_confirm_delete.html", context)


@login_required
def biens_detail(request, pk):
    bien = get_object_or_404(BienImmobilier.objects.select_related("proprietaire"), pk=pk)
    context = {"title": "Détail d'un bien", "bien": bien}
    return render(request, "immobilier/biens_detail.html", context)


@login_required
def proprietaires_liste(request):
    recherche = request.GET.get("q", "").strip()
    proprietaires = Proprietaire.objects.all().order_by("nom_complet")
    if recherche:
        proprietaires = proprietaires.filter(
            Q(nom_complet__icontains=recherche)
            | Q(email__icontains=recherche)
            | Q(telephone__icontains=recherche)
        )
    context = {"title": "Liste des propriétaires", "proprietaires": proprietaires, "q": recherche}
    return render(request, "immobilier/proprietaires_liste.html", context)


@login_required
def proprietaires_create(request):
    if request.method == "POST":
        form = ProprietaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("proprietaires_liste")
    else:
        form = ProprietaireForm()
    context = {"title": "Ajouter un propriétaire", "form": form}
    return render(request, "immobilier/proprietaires_form.html", context)


@login_required
def proprietaires_update(request, pk):
    proprietaire = get_object_or_404(Proprietaire, pk=pk)
    if request.method == "POST":
        form = ProprietaireForm(request.POST, instance=proprietaire)
        if form.is_valid():
            form.save()
            return redirect("proprietaires_liste")
    else:
        form = ProprietaireForm(instance=proprietaire)
    context = {"title": "Modifier un propriétaire", "form": form, "proprietaire": proprietaire}
    return render(request, "immobilier/proprietaires_form.html", context)


@login_required
def proprietaires_delete(request, pk):
    proprietaire = get_object_or_404(Proprietaire, pk=pk)
    if request.method == "POST":
        proprietaire.delete()
        return redirect("proprietaires_liste")
    context = {"title": "Supprimer un propriétaire", "proprietaire": proprietaire}
    return render(request, "immobilier/proprietaires_confirm_delete.html", context)


def _mettre_a_jour_disponibilite_bien(bien):
    a_contrat_actif = bien.contrats.filter(actif=True).exists()
    bien.disponible = not a_contrat_actif
    bien.save(update_fields=["disponible"])


@login_required
def contrats_liste(request):
    recherche = request.GET.get("q", "").strip()
    contrats = ContratLocation.objects.select_related("bien", "bien__proprietaire").order_by("-date_debut")
    if recherche:
        contrats = contrats.filter(
            Q(locataire_nom__icontains=recherche)
            | Q(bien__titre__icontains=recherche)
            | Q(bien__proprietaire__nom_complet__icontains=recherche)
        )
    context = {"title": "Liste des contrats", "contrats": contrats, "q": recherche}
    return render(request, "immobilier/contrats_liste.html", context)


@login_required
def contrats_create(request):
    if request.method == "POST":
        form = ContratLocationForm(request.POST)
        if form.is_valid():
            contrat = form.save()
            _mettre_a_jour_disponibilite_bien(contrat.bien)
            return redirect("contrats_liste")
    else:
        proprietaire_id = request.GET.get("proprietaire")
        initial = {"proprietaire": proprietaire_id} if proprietaire_id else None
        form = ContratLocationForm(initial=initial)
    context = {"title": "Ajouter un contrat", "form": form}
    return render(request, "immobilier/contrats_form.html", context)


@login_required
def contrats_update(request, pk):
    contrat = get_object_or_404(ContratLocation, pk=pk)
    ancien_bien = contrat.bien
    if request.method == "POST":
        form = ContratLocationForm(request.POST, instance=contrat)
        if form.is_valid():
            contrat = form.save()
            _mettre_a_jour_disponibilite_bien(ancien_bien)
            _mettre_a_jour_disponibilite_bien(contrat.bien)
            return redirect("contrats_liste")
    else:
        form = ContratLocationForm(instance=contrat)
    context = {"title": "Modifier un contrat", "form": form, "contrat": contrat}
    return render(request, "immobilier/contrats_form.html", context)


@login_required
def contrats_delete(request, pk):
    contrat = get_object_or_404(ContratLocation.objects.select_related("bien"), pk=pk)
    bien = contrat.bien
    if request.method == "POST":
        contrat.delete()
        _mettre_a_jour_disponibilite_bien(bien)
        return redirect("contrats_liste")
    context = {"title": "Supprimer un contrat", "contrat": contrat}
    return render(request, "immobilier/contrats_confirm_delete.html", context)


@login_required
def contrat_pdf(request, pk):
    contrat = get_object_or_404(ContratLocation.objects.select_related("bien", "bien__proprietaire"), pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrat_{pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Titre
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 80, "CONTRAT DE LOCATION")

    # Ligne de séparation
    p.line(50, height - 95, width - 50, height - 95)

    # Infos contrat
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 130, "Informations du contrat")

    p.setFont("Helvetica", 11)
    p.drawString(50, height - 155, f"Locataire : {contrat.locataire_nom}")
    p.drawString(50, height - 175, f"Bien : {contrat.bien.titre}")
    p.drawString(50, height - 195, f"Adresse : {contrat.bien.adresse}, {contrat.bien.ville}")
    p.drawString(50, height - 215, f"Propriétaire : {contrat.bien.proprietaire.nom_complet}")
    p.drawString(50, height - 235, f"Loyer mensuel : {contrat.bien.loyer_mensuel} FCFA")
    p.drawString(50, height - 255, f"Caution : {contrat.caution} FCFA")
    p.drawString(50, height - 275, f"Date début : {contrat.date_debut}")
    p.drawString(50, height - 295, f"Date fin : {contrat.date_fin}")
    p.drawString(50, height - 315, f"Statut : {'Actif' if contrat.actif else 'Inactif'}")

    # Ligne de séparation
    p.line(50, height - 335, width - 50, height - 335)

    # Signatures
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 370, "Signatures")
    p.setFont("Helvetica", 11)
    
    p.drawString(50, height - 420, f"ropriétaire : {contrat.bien.proprietaire.nom_complet}")

    p.drawString(300, height - 420, f"Locataire : {contrat.locataire_nom}")

    p.showPage()
    p.save()
    return response