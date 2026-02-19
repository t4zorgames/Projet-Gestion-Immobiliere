from django import forms
from .models import BienImmobilier, ContratLocation


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


class ContratLocationForm(forms.ModelForm):
    class Meta:
        model = ContratLocation
        fields = [
            "bien",
            "locataire_nom",
            "date_debut",
            "date_fin",
            "caution",
            "actif",
        ]

    def clean(self):
        cleaned_data = super().clean()
        bien = cleaned_data.get("bien")
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        actif = cleaned_data.get("actif")

        if date_debut and date_fin and date_fin <= date_debut:
            self.add_error("date_fin", "La date de fin doit être après la date de début.")

        if bien and actif:
            contrats_actifs = ContratLocation.objects.filter(bien=bien, actif=True)
            if self.instance.pk:
                contrats_actifs = contrats_actifs.exclude(pk=self.instance.pk)

            if contrats_actifs.exists():
                self.add_error("actif", "Ce bien a déjà un contrat actif.")

        return cleaned_data
