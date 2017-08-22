# Models
"""
This file contains the description of the different models used
in the application. The models are translated automatically into tables
inside the database.
Notice how are the relations between clases are done: models.ForeignKey(...)
"""

from django.db import models
from django.contrib.auth.models import User

class Competicio(models.Model):
    nom = models.CharField(max_length=50)
    titol = models.CharField(max_length=50)
    activa = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.nom)

class Equip(models.Model):
    nom = models.CharField(max_length=50)
    
    def __unicode__(self):
        return unicode(self.nom) 

class EquipCompeticio(models.Model):
    equip = models.ForeignKey(Equip)
    competicio = models.ForeignKey(Competicio)

    def __unicode__(self):
        #return unicode(self.equip)
        return unicode(self.equip) + ' - ' + unicode(self.competicio)
        
class Jugador(models.Model):
    nom = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.nom)

class JugadorEquipCompeticio(models.Model):
    jugador = models.ForeignKey(Jugador)
    equipcompeticio = models.ForeignKey(EquipCompeticio)

    def __unicode__(self):
        #return unicode(self.jugador)
        return unicode(self.jugador) + ' - ' + unicode(self.equipcompeticio) 

        
# We extend the User model of Django
# http://www.b-list.org/weblog/2006/jun/06/django-tips-extending-user-model/
class UserEquipCompeticio(models.Model):
    equipcompeticio = models.ForeignKey(EquipCompeticio)
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return unicode(self.user.username) 

class Jornada(models.Model):
    competicio = models.ForeignKey(Competicio)
    numero = models.PositiveSmallIntegerField()
    data = models.DateField()
    activa = models.BooleanField()
    visible = models.BooleanField()

    def __unicode__(self):
        return unicode(self.competicio) + " J" + unicode(self.numero) + " (" + unicode(self.data) + ")"

class Encontre(models.Model):
    local = models.ForeignKey(EquipCompeticio,related_name="local")
    visitant = models.ForeignKey(EquipCompeticio,related_name="visitant")
    abc = models.ForeignKey(EquipCompeticio,related_name="abc",blank="True",null="True")
    jornada = models.ForeignKey(Jornada)
    # final result of the match
    resultat_local = models.PositiveSmallIntegerField(blank="True",null="True")
    resultat_visitant = models.PositiveSmallIntegerField(blank="True",null="True")
    # games = elevens
    jocs_local = models.PositiveSmallIntegerField(blank="True",null="True")
    jocs_visitant = models.PositiveSmallIntegerField(blank="True",null="True")

    def __unicode__(self):
        return (unicode(self.jornada.competicio) + " J" 
            + unicode(self.jornada.numero) + ": " + unicode(self.local) 
            + " - " + unicode(self.visitant)) 
            
class Individuals(models.Model):
    numero = models.PositiveSmallIntegerField()
    jugador_abc = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_abc")
    jugador_xyz = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_xyz")
    jocs_abc = models.PositiveSmallIntegerField()
    jocs_xyz = models.PositiveSmallIntegerField()
    encontre = models.ForeignKey(Encontre)
    
    def __unicode__(self):
        return (unicode(self.encontre) + " P" + unicode(self.numero) 
            + " " + unicode(self.jugador_abc.jugador) + " - " + unicode(self.jugador_xyz.jugador))

class Dobles(models.Model):
    # No number, only one doublesmatch per TeamMatch
    jugador_abc_1 = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_abc_1")
    jugador_abc_2 = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_abc_2")
    jugador_xyz_1 = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_xyz_1")
    jugador_xyz_2 = models.ForeignKey(JugadorEquipCompeticio,related_name="jugador_xyz_2")
    jocs_abc = models.PositiveSmallIntegerField()
    jocs_xyz = models.PositiveSmallIntegerField()
    encontre = models.ForeignKey(Encontre)
   
    def __unicode__(self):
        return (unicode(self.encontre)  
            + " " + unicode(self.jugador_abc_1.jugador) + "/" + unicode(self.jugador_abc_2.jugador)
            + " - " + unicode(self.jugador_xyz_1.jugador) + "/" + unicode(self.jugador_xyz_2.jugador))

class Ranquingtti(models.Model):
    jugador = models.CharField(max_length=100, blank=True, null=True)
    equip = models.CharField(max_length=100, blank=True, null=True)
    # We create 15 columns and we will only show the useful ones
    torneig1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig4 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig5 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig6 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig7 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig8 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig9 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig10 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig11 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig12 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig13 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig14 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    torneig15 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   
    def __unicode__(self):
        return (unicode(self.jugador) + " " + unicode(self.equip) + " " + unicode(self.total))

class Tornejosranquingtti(models.Model):
    torneig = models.CharField(max_length=100, blank=True, null=True)
   
    def __unicode__(self):
        return (unicode(self.torneig))
