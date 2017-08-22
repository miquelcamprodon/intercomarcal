# Forms
"""
This file contains the definition of the forms used in the application.
Each class is a form with its fields. Notice that the buttons are not
considered part of the classes. They are created at the templates.
"""

# System libraries
import operator
import re

# Django libraries
from django.db import models
from django.forms import ModelForm
from django import forms

# Local libraries
from intercomarcal36.programa.models import (Competicio,Equip,EquipCompeticio,
    Jugador,JugadorEquipCompeticio,UserEquipCompeticio,
    Jornada,Encontre,Individuals,Dobles)
# Language file - Spanish
#from web.clases.languagesp import *


# https://docs.djangoproject.com/en/dev/ref/forms/fields/#modelchoicefield
# Necessitem controlar el text que es visualitza al formulari
# pels jugadors i els equips. Subclassegem ModelChoiceField
# tal com s explica a la documentacio
class MyJugadorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.jugador
        
class MyEquipChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.equip     
        

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class ActaForm(forms.Form):
    equipabc = MyEquipChoiceField(queryset=EquipCompeticio.objects.none())
    equipxyz = MyEquipChoiceField(queryset=EquipCompeticio.objects.all())      
    abc1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr1 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr1 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr2 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr2 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc3 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())        
    xyz3 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr3 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr3 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abcd1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcd2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyzd1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyzd2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcrd = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzrd = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc4 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz4 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr4 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr4 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc5 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz5 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr5 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr5 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc6 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())        
    xyz6 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr6 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr6 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))

    def __init__(self,enc,*args,**kwargs):
        super(ActaForm,self ).__init__(*args,**kwargs) # populates the post

        # Queryset values
        self.fields["equipabc"].queryset = (EquipCompeticio.objects.filter(equip = enc.local.equip, competicio = enc.local.competicio)
                                                | EquipCompeticio.objects.filter(equip = enc.visitant.equip, competicio = enc.local.competicio))
        self.fields["equipxyz"].queryset = self.fields["equipabc"].queryset
        self.fields["abc1"].queryset = (JugadorEquipCompeticio.objects.filter(equipcompeticio = enc.local)
                                                | JugadorEquipCompeticio.objects.filter(equipcompeticio = enc.visitant))
        listfields = ["abc2","abc3","abc4","abc5","abc6","xyz1","xyz2","xyz3","xyz4","xyz5","xyz6",
                    "abcd1","abcd2","xyzd1","xyzd2"]
        for fi in listfields:
            self.fields[fi].queryset = self.fields["abc1"].queryset

        # Initial values  
        if enc.abc != None:
            self.fields["equipabc"].initial = enc.abc.id
            if enc.local != enc.abc:
                self.fields["equipxyz"].initial = enc.local.id
            else:
                self.fields["equipxyz"].initial = enc.visitant.id
        
        for i in range(1,7):
            lind = Individuals.objects.filter(encontre = enc, numero = i)
            if len(lind) > 0:
                ind = lind[0]
                self.fields["abc" + str(i)].initial = ind.jugador_abc.id
                self.fields["xyz" + str(i)].initial = ind.jugador_xyz.id
                self.fields["abcr" + str(i)].initial = ind.jocs_abc
                self.fields["xyzr" + str(i)].initial = ind.jocs_xyz          
                        
        ldob = Dobles.objects.filter(encontre = enc)
        if len(ldob) > 0:
            dob = ldob[0]
            self.fields["abcd1"].initial = dob.jugador_abc_1.id
            self.fields["abcd2"].initial = dob.jugador_abc_2.id
            self.fields["abcrd"].initial = dob.jocs_abc
            self.fields["xyzd1"].initial = dob.jugador_xyz_1.id
            self.fields["xyzd2"].initial = dob.jugador_xyz_2.id
            self.fields["xyzrd"].initial = dob.jocs_xyz

   
            
class ActaFormCD(forms.Form): 
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    equipabc = MyEquipChoiceField(queryset=EquipCompeticio.objects.none())
    equipxyz = MyEquipChoiceField(queryset=EquipCompeticio.objects.all())   
    abc1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr1 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr1 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr2 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr2 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc3 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz3 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr3 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr3 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abcd1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcd2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyzd1 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyzd2 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcrd = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzrd = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc4 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz4 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr4 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr4 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc5 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz5 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr5 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr5 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    abc6 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    xyz6 = MyJugadorChoiceField(queryset=JugadorEquipCompeticio.objects.all())
    abcr6 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))
    xyzr6 = forms.IntegerField(min_value=0,max_value=3,widget=forms.TextInput(attrs={'style':"width: 10px"}))

    def __init__(self,enc,*args,**kwargs):
        super(ActaFormCD,self ).__init__(*args,**kwargs) # populates the post

        # Queryset values
        self.fields["equipabc"].queryset = (EquipCompeticio.objects.filter(equip = enc.local.equip, competicio = enc.local.competicio)
                                                | EquipCompeticio.objects.filter(equip = enc.visitant.equip, competicio = enc.local.competicio))
        self.fields["equipxyz"].queryset = self.fields["equipabc"].queryset
        self.fields["abc1"].queryset = (JugadorEquipCompeticio.objects.filter(equipcompeticio = enc.local)
                                                | JugadorEquipCompeticio.objects.filter(equipcompeticio = enc.visitant))
        listfields = ["abc2","abc3","abc4","abc5","abc6","xyz1","xyz2","xyz3","xyz4","xyz5","xyz6",
                    "abcd1","abcd2","xyzd1","xyzd2"]
        for fi in listfields:
            self.fields[fi].queryset = self.fields["abc1"].queryset

        # Initial values
        if enc.abc != None:
            self.fields["equipabc"].initial = enc.abc.id
            if enc.local != enc.abc:
                self.fields["equipxyz"].initial = enc.local.id
            else:
                self.fields["equipxyz"].initial = enc.visitant.id

        for i in range(1,7):
            lind = Individuals.objects.filter(encontre = enc, numero = i)
            if len(lind) > 0:
                ind = lind[0]
                self.fields["abc" + str(i)].initial = ind.jugador_abc.id
                self.fields["xyz" + str(i)].initial = ind.jugador_xyz.id
                self.fields["abcr" + str(i)].initial = ind.jocs_abc
                self.fields["xyzr" + str(i)].initial = ind.jocs_xyz

        ldob = Dobles.objects.filter(encontre = enc)
        if len(ldob) > 0:
            dob = ldob[0]
            self.fields["abcd1"].initial = dob.jugador_abc_1.id
            self.fields["abcd2"].initial = dob.jugador_abc_2.id
            self.fields["abcrd"].initial = dob.jocs_abc
            self.fields["xyzd1"].initial = dob.jugador_xyz_1.id
            self.fields["xyzd2"].initial = dob.jugador_xyz_2.id
            self.fields["xyzrd"].initial = dob.jocs_xyz
   
