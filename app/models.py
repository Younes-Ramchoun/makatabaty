from django.db import models
from django.contrib.auth.models import User
#pour rendre modification d'un table lorsque une table associé est subit une modification
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver



class Profile(models.Model):
    cni = models.CharField(max_length=12, unique=True,default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def is_staff(self):
        return self.is_admin

class Auteur(models.Model):
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    nationalite = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Domaine(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom
    
class Livre(models.Model):
    titre = models.CharField(max_length=40)
    ISBN = models.CharField(max_length=13, unique=True)
    date_pub = models.DateField()
    description = models.TextField()
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/')
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE)
    domaine = models.ForeignKey(Domaine, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre
    

# Create your models here.
class Emprunt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    livre = models.ManyToManyField(Livre)
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour = models.DateTimeField(blank=True, null=True)
    est_rendu = models.BooleanField(default=False)
    est_prend = models.BooleanField(default=False)
    
    def __str__(self):
        livres_str = ', '.join([livre.titre for livre in self.livre.all()])
        return f"{livres_str}({self.profile.first_name}-{self.profile.last_name})"
    
    def get_livre_emprunte(self):
        return self.livre.first().titre
    
#Dans cette fonction de gestionnaire de signal,
#  nous vérifions si l'emprunt est marqué comme rendu (instance.est_rendu). 
# Si c'est le cas, nous mettons à jour l'attribut disponible du livre associé
#  (instance.livre.disponible = True)  et sauvegardons le livre.
# Définition du signal:
@receiver(post_save, sender=Emprunt)
def update_livre_disponible(sender, instance, **kwargs):
    if instance.est_rendu:
        livre = instance.livre.first()
        livre.disponible = True
        livre.save()

#  rendre le premier livre disponible lorsque l'administrateur supprime un emprunt, vous pouvez utiliser les signaux de pré-suppression (pre_delete) de Django
@receiver(pre_delete, sender=Emprunt)
def update_livre_disponible_on_delete(sender, instance, **kwargs):
    livre = instance.livre.first()
    if livre:
      livre.disponible = True
      livre.save()

