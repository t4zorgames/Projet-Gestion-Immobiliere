from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Proprietaire(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    nom_complet = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nom_complet


class BienImmobilier(models.Model):
    APPARTEMENT = "appartement"
    MAISON = "maison"
    TERRAIN = "terrain"
    LOCAL_COMMERCIAL = "local_commercial"

    YAOUNDE = "yaounde"
    DOUALA = "douala"
    BAFOUSSAM = "bafoussam"
    BAMENDA = "bamenda"
    GAROUA = "garoua"
    MAROUA = "maroua"
    NGAOUNDERE = "ngaoundere"
    BERTOUA = "bertoua"
    EBOLOWA = "ebolowa"
    KRIBI = "kribi"
    LIMBE = "limbe"
    BUEA = "buea"
    KUMBA = "kumba"
    DSCHANG = "dschang"
    NKONGSAMBA = "nkongsamba"
    EDEA = "edea"
    MBALMAYO = "mbalmayo"
    SANGMELIMA = "sangmelima"
    MEIGANGA = "meiganga"
    KOUSSERI = "kousseri"

    TYPE_BIEN_CHOICES = [
        (APPARTEMENT, "Appartement"),
        (MAISON, "Maison"),
        (TERRAIN, "Terrain"),
        (LOCAL_COMMERCIAL, "Local commercial"),
    ]

    VILLE_CHOICES = [
        (YAOUNDE, "Yaoundé"),
        (DOUALA, "Douala"),
        (BAFOUSSAM, "Bafoussam"),
        (BAMENDA, "Bamenda"),
        (GAROUA, "Garoua"),
        (MAROUA, "Maroua"),
        (NGAOUNDERE, "Ngaoundéré"),
        (BERTOUA, "Bertoua"),
        (EBOLOWA, "Ebolowa"),
        (KRIBI, "Kribi"),
        (LIMBE, "Limbé"),
        (BUEA, "Buéa"),
        (KUMBA, "Kumba"),
        (DSCHANG, "Dschang"),
        (NKONGSAMBA, "Nkongsamba"),
        (EDEA, "Edéa"),
        (MBALMAYO, "Mbalmayo"),
        (SANGMELIMA, "Sangmélima"),
        (MEIGANGA, "Meiganga"),
        (KOUSSERI, "Kousséri"),
    ]

    titre = models.CharField(max_length=150)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100, choices=VILLE_CHOICES)
    superficie_m2 = models.PositiveIntegerField()
    loyer_mensuel = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    type_bien = models.CharField(max_length=30, choices=TYPE_BIEN_CHOICES)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE, related_name="biens")
    disponible = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    # Owners can require contract acceptance; the contract will be prefilled from owner/property data.
    exige_validation_contrat = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class ContratLocation(models.Model):
    bien = models.ForeignKey(BienImmobilier, on_delete=models.CASCADE, related_name="contrats")
    locataire_nom = models.CharField(max_length=120)
    locataire_telephone = models.CharField(max_length=20, blank=True)
    locataire_email = models.EmailField(blank=True)
    locataire_info = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    caution = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_debut"]

    def __str__(self):
        return f"{self.locataire_nom} - {self.bien.titre}"
