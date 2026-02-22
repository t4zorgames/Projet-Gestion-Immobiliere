from django import forms
from django.db.models import Q
from .models import BienImmobilier, ContratLocation, Proprietaire
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BienImmobilierForm(forms.ModelForm):
    class Meta:
        model = BienImmobilier
        fields = [
            "titre",
            "adresse",
            "ville",
            "superficie_m2",
            "loyer_mensuel",
            "type_bien",
            "proprietaire",
            "disponible",
            "exige_validation_contrat",
        ]


class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = Proprietaire
        fields = ["nom_complet", "email", "telephone"]


class ContratLocationForm(forms.ModelForm):
    # proprietaire is an extra field to help filter 'bien' choices in the form
    proprietaire = forms.ModelChoiceField(
        queryset=Proprietaire.objects.all().order_by("nom_complet"),
        required=True,
        label="Propriétaire",
    )
    accepte_contrat = forms.BooleanField(
        required=False,
        label="J'accepte le contrat du propriétaire",
        help_text="Cochez si vous acceptez les conditions du contrat pré-rempli.",
    )

    class Meta:
        model = ContratLocation
        # 'proprietaire' is NOT a model field on ContratLocation, so remove it from Meta.fields
        fields = [
            "bien",
            "locataire_nom",
            "locataire_telephone",
            "locataire_email",
            "locataire_info",
            "date_debut",
            "date_fin",
            "caution",
            "actif",
        ]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bien"].queryset = BienImmobilier.objects.none()

        # prefer POST data, then initial, then instance
        selected_owner_id = self.data.get("proprietaire") or self.initial.get("proprietaire")

        if self.instance and self.instance.pk:
            current_owner_id = self.instance.bien.proprietaire_id
            self.fields["proprietaire"].initial = current_owner_id
            if not selected_owner_id:
                selected_owner_id = current_owner_id

        try:
            selected_owner_id = int(selected_owner_id) if selected_owner_id else None
        except (TypeError, ValueError):
            selected_owner_id = None

        if selected_owner_id:
            self.fields["bien"].queryset = BienImmobilier.objects.filter(
                Q(proprietaire_id=selected_owner_id, disponible=True)
                | Q(pk=getattr(self.instance, "bien_id", None))
            ).order_by("titre")

        if self.instance and self.instance.pk and not self.fields["bien"].queryset.exists():
            # allow current bien even if not disponible
            self.fields["bien"].queryset = BienImmobilier.objects.filter(
                Q(disponible=True) | Q(pk=self.instance.bien_id)
            ).order_by("titre")

    def clean(self):
        cleaned_data = super().clean()
        bien = cleaned_data.get("bien")
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        actif = cleaned_data.get("actif")
        accepte_contrat = cleaned_data.get("accepte_contrat")

        if date_debut and date_fin and date_fin <= date_debut:
            self.add_error("date_fin", "La date de fin doit être après la date de début.")

        proprietaire = cleaned_data.get("proprietaire")

        if bien and proprietaire and bien.proprietaire_id != proprietaire.id:
            self.add_error("bien", "Le bien sélectionné ne correspond pas au propriétaire choisi.")

        if bien and actif:
            contrats_actifs = ContratLocation.objects.filter(bien=bien, actif=True)
            if self.instance.pk:
                contrats_actifs = contrats_actifs.exclude(pk=self.instance.pk)

            if contrats_actifs.exists():
                self.add_error("actif", "Ce bien a déjà un contrat actif.")

        # If the selected bien has a contract template and requires validation,
        # ensure the renter accepted it.
        if bien and getattr(bien, "exige_validation_contrat", False):
            if not accepte_contrat:
                self.add_error("accepte_contrat", "Vous devez accepter le contrat du propriétaire pour louer ce bien.")

        return cleaned_data

    def save(self, commit=True):
        # instance is a ContratLocation; the form uses the 'bien' field directly.
        contrat = super().save(commit=False)
        # No extra handling needed for proprietaire because we validate bien/proprietaire in clean()
        if commit:
            contrat.save()
        return contrat


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=150)
    is_proprietaire = forms.BooleanField(required=False, label="Je suis propriétaire")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            # Create a Proprietaire only if the registrant indicates they are an owner
            if self.cleaned_data.get("is_proprietaire"):
                Proprietaire.objects.get_or_create(
                    user=user,
                    defaults={
                        "nom_complet": f"{user.first_name} {user.last_name}".strip() or user.username,
                        "email": user.email,
                    },
                )
        return user
