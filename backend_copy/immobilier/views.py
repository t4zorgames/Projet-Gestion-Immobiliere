from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from .forms import BienImmobilierForm, ContratLocationForm, ProprietaireForm, UserRegistrationForm
from .models import BienImmobilier, ContratLocation, Proprietaire
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


@login_required
def dashboard(request):
    # If the logged-in user is a proprietor, show owner dashboard with their biens and demandes
    try:
        proprietaire = Proprietaire.objects.get(user=request.user)
    except Proprietaire.DoesNotExist:
        proprietaire = None

    if proprietaire:
        biens = BienImmobilier.objects.filter(proprietaire=proprietaire).order_by('-cree_le')
        demandes = ContratLocation.objects.select_related('bien').filter(bien__proprietaire=proprietaire).order_by('-date_debut')
        total_biens = biens.count()
        disponibles = biens.filter(disponible=True).count()
        indisponibles = total_biens - disponibles
        demandes_count = demandes.count()
        # breakdown by city
        villes_qs = biens.values('ville').annotate(count=Count('id')).order_by('-count')
        villes = [v['ville'] for v in villes_qs]
        villes_counts = [v['count'] for v in villes_qs]

        context = {
            'title': 'Espace propriétaire',
            'proprietaire': proprietaire,
            'biens': biens,
            'demandes': demandes,
            'stats': {
                'total_biens': total_biens,
                'disponibles': disponibles,
                'indisponibles': indisponibles,
                'demandes': demandes_count,
            },
            'villes': villes,
            'villes_counts': villes_counts,
        }
        return render(request, 'immobilier/owner_dashboard.html', context)

    # Otherwise show a simple user (locataire) dashboard with recent biens and user's contrats
    recent_biens = BienImmobilier.objects.filter(disponible=True).order_by('-cree_le')[:10]
    user_contrats = ContratLocation.objects.filter(locataire_email=request.user.email).order_by('-date_debut')
    # stats for tenant
    total_available = BienImmobilier.objects.filter(disponible=True).count()
    # compute city breakdown from the full available set (not from sliced queryset)
    villes_qs = BienImmobilier.objects.filter(disponible=True).values('ville').annotate(count=Count('id')).order_by('-count')[:5]
    villes = [v['ville'] for v in villes_qs]
    villes_counts = [v['count'] for v in villes_qs]
    context = {
        'title': 'Espace locataire',
        'recent_biens': recent_biens,
        'user_contrats': user_contrats,
        'stats': {
            'total_available': total_available,
        },
        'villes': villes,
        'villes_counts': villes_counts,
    }
    return render(request, 'immobilier/user_dashboard.html', context)


from django.contrib import messages


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add a confirmation message and redirect to login so the user can authenticate
            messages.success(request, "Compte créé avec succès. Veuillez vous connecter.")
            return redirect("connexion")
    else:
        form = UserRegistrationForm()

    context = {
        "title": "Inscription",
        "form": form,
    }
    return render(request, "registration/register.html", context)


@login_required
def page_placeholder(request, title, description, pk=None):
    context = {
        "title": title,
        "description": description,
        "pk": pk,
    }
    return render(request, "immobilier/page_placeholder.html", context)


def _paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def biens_liste(request):
    recherche = request.GET.get("q", "").strip()
    biens = BienImmobilier.objects.select_related("proprietaire").order_by("-cree_le")

    if recherche:
        biens = biens.filter(Q(titre__icontains=recherche) | Q(ville__icontains=recherche))

    page_obj = _paginate_queryset(request, biens)

    context = {
        "title": "Liste des biens",
        "biens": page_obj,
        "q": recherche,
    }
    return render(request, "immobilier/biens_liste.html", context)


@login_required
def biens_create(request):
    # Only allow creation for staff or users already linked to a Proprietaire
    from .models import Proprietaire as _Proprietaire

    try:
        is_prop = _Proprietaire.objects.filter(user=request.user).exists()
    except Exception:
        is_prop = False

    if not request.user.is_staff and not is_prop:
        return redirect('devenir_proprietaire')

    if request.method == "POST":
        form = BienImmobilierForm(request.POST, request.FILES)
        if not request.user.is_staff:
            form.fields.pop("proprietaire", None)

        if form.is_valid():
            bien = form.save(commit=False)
            proprietaire, _ = Proprietaire.objects.get_or_create(
                user=request.user,
                defaults={
                    "nom_complet": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    "email": request.user.email,
                },
            )
            bien.proprietaire = proprietaire
            bien.save()
            return redirect("biens_liste")
    else:
        form = BienImmobilierForm()
        if not request.user.is_staff:
            form.fields.pop("proprietaire", None)

    context = {
        "title": "Ajouter un bien",
        "form": form,
    }
    return render(request, "immobilier/biens_form.html", context)


@login_required
def biens_update(request, pk):
    bien = get_object_or_404(BienImmobilier, pk=pk)

    # Only staff or owner may edit
    if not request.user.is_staff and (not bien.proprietaire or bien.proprietaire.user_id != request.user.id):
        raise PermissionDenied()

    if request.method == "POST":
        form = BienImmobilierForm(request.POST, request.FILES, instance=bien)
        if not request.user.is_staff:
            form.fields.pop("proprietaire", None)
        if form.is_valid():
            form.save()
            return redirect("biens_liste")
    else:
        form = BienImmobilierForm(instance=bien)
        if not request.user.is_staff:
            form.fields.pop("proprietaire", None)

    context = {
        "title": "Modifier un bien",
        "form": form,
        "bien": bien,
    }
    return render(request, "immobilier/biens_form.html", context)


@login_required
def biens_delete(request, pk):
    bien = get_object_or_404(BienImmobilier, pk=pk)

    # Only staff or owner may delete
    if not request.user.is_staff and (not bien.proprietaire or bien.proprietaire.user_id != request.user.id):
        raise PermissionDenied()

    if request.method == "POST":
        bien.delete()
        return redirect("biens_liste")

    context = {
        "title": "Supprimer un bien",
        "bien": bien,
    }
    return render(request, "immobilier/biens_confirm_delete.html", context)


def biens_detail(request, pk):
    bien = get_object_or_404(BienImmobilier.objects.select_related("proprietaire"), pk=pk)
    context = {
        "title": "Détail d'un bien",
        "bien": bien,
    }
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

    page_obj = _paginate_queryset(request, proprietaires)

    context = {
        "title": "Liste des propriétaires",
        "proprietaires": page_obj,
        "q": recherche,
    }
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

    context = {
        "title": "Ajouter un propriétaire",
        "form": form,
    }
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

    context = {
        "title": "Modifier un propriétaire",
        "form": form,
        "proprietaire": proprietaire,
    }
    return render(request, "immobilier/proprietaires_form.html", context)


@login_required
def proprietaires_delete(request, pk):
    proprietaire = get_object_or_404(Proprietaire, pk=pk)

    if request.method == "POST":
        proprietaire.delete()
        return redirect("proprietaires_liste")

    context = {
        "title": "Supprimer un propriétaire",
        "proprietaire": proprietaire,
    }
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

    page_obj = _paginate_queryset(request, contrats)

    context = {
        "title": "Liste des contrats",
        "contrats": page_obj,
        "q": recherche,
    }
    return render(request, "immobilier/contrats_liste.html", context)


@login_required
def proprietaire_demandes(request):
    # get Proprietaire linked to logged in user
    try:
        proprietaire = Proprietaire.objects.get(user=request.user)
    except Proprietaire.DoesNotExist:
        return HttpResponseForbidden("Vous n'êtes pas associé à un propriétaire.")

    demandes = ContratLocation.objects.select_related('bien').filter(bien__proprietaire=proprietaire).order_by('-date_debut')
    context = {
        'title': 'Demandes reçues',
        'demandes': demandes,
    }
    return render(request, 'immobilier/proprietaire_demandes.html', context)


@login_required
def devenir_proprietaire(request):
    # Create a Proprietaire record for the logged-in user and redirect to add a bien
    from .models import Proprietaire

    if request.method == 'POST':
        proprietaire, created = Proprietaire.objects.get_or_create(
            user=request.user,
            defaults={
                'nom_complet': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
            }
        )
        return redirect('biens_ajouter')

    return render(request, 'immobilier/become_proprietaire.html', {'title': 'Devenir propriétaire'})


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

    context = {
        "title": "Ajouter un contrat",
        "form": form,
    }
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

    context = {
        "title": "Modifier un contrat",
        "form": form,
        "contrat": contrat,
    }
    return render(request, "immobilier/contrats_form.html", context)


@login_required
def contrats_delete(request, pk):
    contrat = get_object_or_404(ContratLocation.objects.select_related("bien"), pk=pk)
    bien = contrat.bien

    if request.method == "POST":
        contrat.delete()
        _mettre_a_jour_disponibilite_bien(bien)
        return redirect("contrats_liste")

    context = {
        "title": "Supprimer un contrat",
        "contrat": contrat,
    }
    return render(request, "immobilier/contrats_confirm_delete.html", context)
