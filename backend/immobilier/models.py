from django.db import models


class Proprietaire(models.Model):
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

	TYPE_BIEN_CHOICES = [
		(APPARTEMENT, "Appartement"),
		(MAISON, "Maison"),
		(TERRAIN, "Terrain"),
		(LOCAL_COMMERCIAL, "Local commercial"),
	]

	titre = models.CharField(max_length=150)
	adresse = models.CharField(max_length=255)
	ville = models.CharField(max_length=100)
	superficie_m2 = models.PositiveIntegerField()
	loyer_mensuel = models.DecimalField(max_digits=10, decimal_places=2)
	type_bien = models.CharField(max_length=30, choices=TYPE_BIEN_CHOICES)
	proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE, related_name="biens")
	disponible = models.BooleanField(default=True)
	cree_le = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.titre


class ContratLocation(models.Model):
	bien = models.ForeignKey(BienImmobilier, on_delete=models.CASCADE, related_name="contrats")
	locataire_nom = models.CharField(max_length=120)
	date_debut = models.DateField()
	date_fin = models.DateField()
	caution = models.DecimalField(max_digits=10, decimal_places=2)
	actif = models.BooleanField(default=True)

	class Meta:
		ordering = ["-date_debut"]

	def __str__(self):
		return f"{self.locataire_nom} - {self.bien.titre}"
