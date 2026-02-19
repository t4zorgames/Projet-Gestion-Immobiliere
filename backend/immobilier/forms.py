from django import forms
from .models import BienImmobilier


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
