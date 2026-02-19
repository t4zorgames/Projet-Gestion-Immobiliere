from django import forms
from django.db.models import Q
from .models import BienImmobilier, ContratLocation, Proprietaire


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
        ]


class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = Proprietaire
        fields = ["nom_complet", "email", "telephone"]


class ContratLocationForm(forms.ModelForm):
    proprietaire = forms.ModelChoiceField(
        queryset=Proprietaire.objects.all().order_by("nom_complet"),
        required=True,
        label="Propriétaire",
    )

    class Meta:
        model = ContratLocation
        fields = [
            "proprietaire",
            "bien",
            "locataire_nom",
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

        selected_owner_id = self.data.get("proprietaire") or self.initial.get("proprietaire")

        if self.instance and self.instance.pk:
            current_owner_id = self.instance.bien.proprietaire_id
            self.fields["proprietaire"].initial = current_owner_id
            selected_owner_id = selected_owner_id or current_owner_id

        if selected_owner_id:
            self.fields["bien"].queryset = BienImmobilier.objects.filter(
                Q(proprietaire_id=selected_owner_id, disponible=True)
                | Q(pk=getattr(self.instance, "bien_id", None))
            ).order_by("titre")

        if self.instance and self.instance.pk:
            self.fields["bien"].queryset = BienImmobilier.objects.filter(
                Q(disponible=True) | Q(pk=self.instance.bien_id)
            ).order_by("titre")

    def clean(self):
        cleaned_data = super().clean()
        bien = cleaned_data.get("bien")
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        actif = cleaned_data.get("actif")

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

        return cleaned_data
