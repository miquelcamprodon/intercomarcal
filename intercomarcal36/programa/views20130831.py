# Views
"""
intercomarcal - programa application
"""

"""
This file contains the views which are used in the application.
Each view is a request function
    def view(request): 
and must return a response to the request. This response can be done
in two ways:
    * HttpResponseRedirect, which simply redirects to a web page.
        To avoid hardcoding the URL, we may use reverse().
    * render_to_response, which redirects to a web page, but it includes
        objects that must be rendered before showing the response.
"""

"""
Scheme to show a form
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            process_form()
            return HttpResponseRedirect('/classes/' + classe_id + '/')
            return HttpResponseRedirect(reverse(...,{'classe_id':classe_id})')
        else:
            return render_to_response('classes/info.html',
                {'form':form,'classe':c}, 
                context_instance=RequestContext(request))
    else:
        form = ClassForm()
        return render_to_response('classes/info.html',
                {'form':form,'classe':c}, 
                context_instance=RequestContext(request))
"""

# System libraries
import datetime
import re
    
# Django libraries
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.db.models import Q
#from django.views.decorators.csrf import csrf_protect

# Local libraries
from intercomarcal.programa.models import (Competicio,Equip,EquipCompeticio,
    Jugador,JugadorEquipCompeticio,UserEquipCompeticio,
    Jornada,Encontre,Individuals,Dobles)
from intercomarcal.programa.forms import ActaForm,LoginForm,ActaFormCD
# Language file - Catalan
#from web.clases.languagesp import *

def index(request):
    return render_to_response('programa/index.html')



def get_equips_descansa(competicio):
    # Aconseguim tots els equips i totes les jornades

    num_jor = len(Jornada.objects.filter(competicio__nom = competicio.nom).order_by("numero"))
    primera_jor = 1
    if num_jor > 0:
        primera_jor = Jornada.objects.filter(competicio__nom = competicio.nom).order_by("numero")[0].numero

    equips = EquipCompeticio.objects.filter(competicio__nom = competicio.nom)
    num_equips = len(equips)
    
    ldescansa = []
    
    if (num_equips % 2 != 0):
        for i in range(primera_jor,primera_jor + num_jor + 1):
            jornada = Jornada.objects.filter(competicio__nom = competicio.nom,numero = i)
            
            if len(jornada) > 0:
                encontres = jornada[0].encontre_set.all()
                 
                equipsjor = []             
                for enc in encontres:
                    equipsjor.append(enc.local.equip.nom)
                    equipsjor.append(enc.visitant.equip.nom)
                fi = 0
                for equip in equips:
                    if (equip.equip.nom not in equipsjor) and (fi == 0):
                        ldescansa.append(equip.equip.nom)
                        fi = 1   

    return ldescansa

def calendari(request,comp_nom):
    listj = Jornada.objects.filter(competicio__nom = comp_nom).order_by("numero")
    liste = EquipCompeticio.objects.filter(competicio__nom = comp_nom)
    lcomp = Competicio.objects.filter(nom = comp_nom)
    if len(lcomp) > 0:
        comp = lcomp[0]
    else:
        comp = "Competicio no existent"

    ldescansa = get_equips_descansa(lcomp[0])

    ljordesc = []
    for i in range(0,len(listj)):
        elem = {}
        elem['jornada'] = listj[i]
        if len(ldescansa) > i:
            elem['descansa'] = ldescansa[i]
        ljordesc.append(elem)

    return render_to_response('programa/calendari.html',
        {'competicio':comp,'ljordesc':ljordesc,'equip_descansa':(len(ldescansa) > 0)},
        context_instance=RequestContext(request)) 


def calendari_entrar(request,comp_nom):
    listj = Jornada.objects.filter(competicio__nom = comp_nom).order_by("numero")
    lcomp = Competicio.objects.filter(nom = comp_nom)
    if len(lcomp) > 0:
        comp = lcomp[0]
    else:
        comp = "Competicio no existent"

    ldescansa = get_equips_descansa(lcomp[0]);

    ljordesc = []
    for i in range(0,len(listj)):
        elem = {}
        elem['jornada'] = listj[i]
        if len(ldescansa) > i:
            elem['descansa'] = ldescansa[i]
        ljordesc.append(elem)

    return render_to_response('programa/calendari_entrar.html',
        {'competicio':comp,'ljordesc':ljordesc,'equip_descansa':(len(ldescansa) > 0)},
        context_instance=RequestContext(request))
        
        
def ordena_subclassificacio(loteams_ret,iii,jjj,lcomps):
    # lcomps es un vector amb el llistat de competicions a analitzar

    # Tots els equips
    equips = []
    
    for j in range(iii,jjj+1):
        equips.append(loteams_ret[j][0])
    # Tots els partits
    enccomp = Encontre.objects.filter(local__in=equips,
            jornada__competicio__nom__in=lcomps).filter(visitant__in=equips,jornada__competicio__nom__in=lcomps)

    lequips = {}
    for e in equips:
        # Initialize
        lequips[e] = {}
        lequips[e]['pj'] = 0
        lequips[e]['pg'] = 0
        lequips[e]['pp'] = 0
        lequips[e]['puf'] = 0 # punts - partides guanyades ex: 5-2, 4-3 ...
        lequips[e]['puc'] = 0
        lequips[e]['sf'] = 0
        lequips[e]['sc'] = 0
        lequips[e]['punts'] = 0
        # Local games
        enclist = enccomp.filter(local__equip=e.equip)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_local
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_visitant                    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_local
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_visitant
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0

        # Visitor games
        enclist = enccomp.filter(visitant__equip=e.equip)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_visitant
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_local    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_visitant
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_local
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2
                    
        # Now we build the classification table. Inverse order
        loteams = lequips.items()    
        # Fourth criteria: sf/sc in the matches of the teams implicated
        loteams.sort(key=lambda x:-(x[1]['sf']/(x[1]['sc'] + 0.00001)))         
        # Third criteria: puf / puc
        loteams.sort(key=lambda x:-(x[1]['puf']/(x[1]['puc'] + 0.00001)))  
        # Second criteria: points in the matches of the teams implicated
        loteams.sort(key=lambda x:-x[1]['punts'])        
 
    # Escrivim a loteams_ret
    for i in range(0,len(loteams)):
        team = loteams[i][0]
        aux = loteams_ret[iii + i]
        
        k = 0
        trobat = loteams_ret[iii + k][0] == team;
        while not trobat and k <= jjj:
            k = k + 1
            trobat = loteams_ret[iii + k][0] == team;
        loteams_ret[iii + i] = loteams_ret[iii + k]
        loteams_ret[iii + k] = aux
    
    return loteams_ret
        
        
def classificacio(request,comp_nom):
    # 2010
    if comp_nom == "20101fA" or comp_nom == "20101fB":
        return classificacio_1_lligueta(request,comp_nom)
    elif comp_nom == "20102f1" or comp_nom == "20102f2":
        return classificacio_2_lligueta(request,comp_nom)
    # 2011    
    elif comp_nom == "20111f":
        return classificacio_1_lligueta(request,comp_nom)
    elif comp_nom == "20112f1" or comp_nom == "20112f2":
        return classificacio_2_lligueta(request,comp_nom)
    # 2012    
    elif comp_nom == "20121f":
        return classificacio_1_lligueta(request,comp_nom)
    elif comp_nom == "20122f1" or comp_nom == "20122f2" or comp_nom == "20122f3":
        return classificacio_2_lligueta(request,comp_nom)


def classificacio_1_lligueta(request,comp_nom):
    equips = EquipCompeticio.objects.filter(competicio__nom = comp_nom)
    lequips = {}

    # Encontres of the competition
    enccomp = Encontre.objects.filter(jornada__competicio__nom = comp_nom).order_by("jornada__numero")
    for e in equips:
        # Initialize
        lequips[e] = {}
        lequips[e]['pj'] = 0
        lequips[e]['pg'] = 0
        lequips[e]['pp'] = 0
        lequips[e]['puf'] = 0 # punts - partides guanyades ex: 5-2, 4-3 ...
        lequips[e]['puc'] = 0
        lequips[e]['sf'] = 0
        lequips[e]['sc'] = 0
        lequips[e]['punts'] = 0
        # Local games
        enclist = enccomp.filter(local__equip=e.equip)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_local
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_visitant                    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_local
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_visitant
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0

        # Visitor games
        enclist = enccomp.filter(visitant__equip=e.equip)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_visitant
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_local    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_visitant
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_local
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2

    # Now we build the classification table. Inverse order
    loteams = lequips.items()
    # Fifth criteria: sf / sc
    loteams.sort(key=lambda x:-(x[1]['sf']/(x[1]['sc'] + 0.00001)))
    # Fourth criteria: sf/sc in the matches of the teams implicated
    # Fourth criteria: sf - sc
    loteams.sort(key=lambda x:-(x[1]['sf']-x[1]['sc']))         
    # Third criteria: puf/puc in the matches of the teams implicated
    # Third criteria: puf / puc
    loteams.sort(key=lambda x:-(x[1]['puf']/(x[1]['puc'] + 0.00001)))
    # Second criteria: points in the matches of the teams implicated
    # Second criteria: puf - puc
    loteams.sort(key=lambda x:-(x[1]['puf']-x[1]['puc'])) 
    # First criteria: number of points
    loteams.sort(key=lambda x:-x[1]['punts']) 
    # Build table

    
    # Ordenem els equips entre ells
    puntsant = loteams[0][1]['punts']
    indexant = 0
    for k in range(1,len(loteams)):
        if loteams[k][1]['punts'] != puntsant:
            if (k - indexant - 1) > 0:
                # Ordenar entre les posicions indexant i (k - 1)
                loteams = ordena_subclassificacio(loteams,indexant,k-1,[comp_nom])
            indexant = k
            puntsant = loteams[k][1]['punts']
    # Quan arribem al final mirem l'ultim element
    if puntsant == loteams[len(loteams)-1][1]['punts']:
        # Ordenar entre les posicions indexant i len(loteams) - 1
        loteams = ordena_subclassificacio(loteams,indexant,len(loteams)-1,[comp_nom])
    
    
    tclass = []
    for e in loteams:
        tclass.append({"equipcompeticio":e[0],"pj":e[1]['pj'],"pg":e[1]['pg'],"pp":e[1]['pp'],"puf":e[1]['puf'],"puc":e[1]['puc'],"sf":e[1]['sf'],"sc":e[1]['sc'],"punts":e[1]['punts']})

    return render_to_response('programa/classificacio.html',
        {'classificacio':tclass},
        context_instance=RequestContext(request))


def classificacio_2_lligueta(request,comp_nom):
    # Afegim les lliguetes previes de cada lligueta
    dic_1_lligueta = {}
    dic_1_lligueta['20102f1'] = ['20101fA','20101fB']
    dic_1_lligueta['20102f2'] = ['20101fA','20101fB']
    
    dic_1_lligueta['20112f1'] = ['20111f']
    dic_1_lligueta['20112f2'] = ['20111f']
    
    dic_1_lligueta['20122f1'] = ['20121f']
    dic_1_lligueta['20122f2'] = ['20121f']
    dic_1_lligueta['20122f3'] = ['20121f']        

    # Codi
    lcomps = dic_1_lligueta[comp_nom]
    lcomps.append(comp_nom)
   
    equips = EquipCompeticio.objects.filter(competicio__nom = comp_nom)
    lequips = {}

    # Encontres of the competition
    enccomp = Encontre.objects.filter(jornada__competicio__nom__in=lcomps).order_by("jornada__numero")

    for e in equips:
        # Initialize
        lequips[e] = {}
        lequips[e]['pj'] = 0
        lequips[e]['pg'] = 0
        lequips[e]['pp'] = 0
        lequips[e]['puf'] = 0 # punts - partides guanyades ex: 5-2, 4-3 ...
        lequips[e]['puc'] = 0
        lequips[e]['sf'] = 0
        lequips[e]['sc'] = 0
        lequips[e]['punts'] = 0
        # Local games
        temp = e.equip
        enclist = enccomp.filter(local__equip=temp)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_local
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_visitant                    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_local
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_visitant
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0

        # Visitor games
        enclist = enccomp.filter(visitant__equip=e.equip)
        for enc in enclist:
            if enc.jocs_local != None:
                lequips[e]['puf'] = lequips[e]['puf'] + enc.resultat_visitant
                lequips[e]['puc'] = lequips[e]['puc'] + enc.resultat_local    
                lequips[e]['sf'] = lequips[e]['sf'] + enc.jocs_visitant
                lequips[e]['sc'] = lequips[e]['sc'] + enc.jocs_local
                if (enc.resultat_local >= 4):
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pp'] = lequips[e]['pp'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 0
                else:
                    lequips[e]['pj'] = lequips[e]['pj'] + 1
                    lequips[e]['pg'] = lequips[e]['pg'] + 1
                    lequips[e]['punts'] = lequips[e]['punts'] + 2

    # Now we build the classification table. Inverse order
    loteams = lequips.items()
    if len(loteams) > 0:
        # Fifth criteria: sf / sc
        loteams.sort(key=lambda x:-(x[1]['sf']/(x[1]['sc'] + 0.00001)))
        # Fourth criteria: sf/sc in the matches of the teams implicated
        # Fourth criteria: sf - sc
        loteams.sort(key=lambda x:-(x[1]['sf']-x[1]['sc']))         
        # Third criteria: puf/puc in the matches of the teams implicated
        # Third criteria: puf / puc
        loteams.sort(key=lambda x:-(x[1]['puf']/(x[1]['puc'] + 0.00001)))
        # Second criteria: points in the matches of the teams implicated
        # Second criteria: puf - puc
        loteams.sort(key=lambda x:-(x[1]['puf']-x[1]['puc'])) 
        # First criteria: number of points
        loteams.sort(key=lambda x:-x[1]['punts']) 
        # Build table
    
        # Ordenem els equips entre ells
        puntsant = loteams[0][1]['punts']
        indexant = 0
        for k in range(1,len(loteams)):
            if loteams[k][1]['punts'] != puntsant:
                if (k - indexant - 1) > 0:
                    # Ordenar entre les posicions indexant i (k - 1)
                    loteams = ordena_subclassificacio(loteams,indexant,k-1,lcomps)
                indexant = k
                puntsant = loteams[k][1]['punts']
        # Quan arribem al final mirem l'ultim element
        if puntsant == loteams[len(loteams)-1][1]['punts']:
            # Ordenar entre les posicions indexant i len(loteams) - 1
            loteams = ordena_subclassificacio(loteams,indexant,len(loteams)-1,lcomps)
   
    
    tclass = []
    for e in loteams:
        tclass.append({"equipcompeticio":e[0],"pj":e[1]['pj'],"pg":e[1]['pg'],"pp":e[1]['pp'],"puf":e[1]['puf'],"puc":e[1]['puc'],"sf":e[1]['sf'],"sc":e[1]['sc'],"punts":e[1]['punts']})

    return render_to_response('programa/classificacio.html',
        {'classificacio':tclass},
        context_instance=RequestContext(request))

        
def ranquing(request,comp_nom):
    # If comp_nom == '20101fAB' then we want to show matches
    # in competitions '20101fA' or '20101fB'     
    if comp_nom == '20101fAB':
        l_comp_1f = ['20101fA','20101fB']
        return ranquing_primera_fase(request,comp_nom,l_comp_1f)

    # If comp_nom == '20102f12' then we want to show matches
    # in competitions '20101fA','20101fB','20102f1','20102f2'
    # if competition == '20102f1' then win: 2, loss: -1
    # if competition == '20102f2' then win: 1, loss: -1    

    elif comp_nom == '20102f12':
        l_comp_12f = ['20101fA','20101fB','20102f1','20102f2']
        l_comp_2punts = ['20101fA','20101fB','20102f1']
        l_comp_1punt = ['20102f2']
        return ranquing_segona_fase(request,comp_nom,l_comp_12f,l_comp_2punts,l_comp_1punt)    

    if comp_nom == '20111f':    
        l_comp_1f = ['20111f']
        return ranquing_primera_fase(request,comp_nom,l_comp_1f)
    elif comp_nom == '20112f12':
        l_comp_12f = ['20111f','20112f1','20112f2']
        l_comp_2punts = ['20111f','20112f1']
        l_comp_1punt = ['20112f2']
        return ranquing_segona_fase(request,comp_nom,l_comp_12f,l_comp_2punts,l_comp_1punt,l_comp_1_5punts)       

    if comp_nom == '20121f':    
        l_comp_1f = ['20121f']
        return ranquing_primera_fase(request,comp_nom,l_comp_1f)
    elif comp_nom == '20122f123':
        l_comp_12f = ['20121f','20122f1','20122f2','20122f3']
        l_comp_2punts = ['20121f','20122f1']
        l_comp_1_5punts = ['20122f2']
        l_comp_1punt = ['20122f3']
        #return ranquing_segona_fase(request,comp_nom,l_comp_12f,l_comp_2punts,l_comp_1punt)       
        return ranquing_utilitzant_precalcula(request)


def ranquing_primera_fase(request,comp_nom,l_comp_1f,precalcula=False):        
    # Get all players that have played at least one match
    lj = set()
    ljug = {}
        
    # All Individuals (matches)
    enclist = Individuals.objects.filter(
            #encontre__jornada__competicio__nom__in = ['20101fA','20101fB'])
            encontre__jornada__competicio__nom__in = l_comp_1f)
                
    #for p in Individuals.objects.filter(encontre__jornada__competicio__nom = comp_nom):
    #for p in Individuals.objects.filter(encontre__jornada__competicio__nom__in = ['20101fA','20101fB']):
    #for p in Individuals.objects.filter(encontre__jornada__competicio__nom__in = l_comp_1f):

    
    # Loop by partit (Individual), we hope it is more efficient    
    for enc in enclist:
        # note: player is a JugadorEquipCompeticio, as we expect
        # abc player
        e = enc.jugador_abc.jugador    
        if e not in lj:
            # Initialize
            lj.add(e)
            ljug[e] = {}
            ljug[e]['equip'] = enc.jugador_abc.equip.nom
            ljug[e]['equip_id'] = enc.jugador_abc.equip.id
            ljug[e]['pj'] = 0
            ljug[e]['pg'] = 0
            ljug[e]['pp'] = 0
            ljug[e]['sf'] = 0
            ljug[e]['sc'] = 0
            ljug[e]['punts'] = 0
        # Update
        ljug[e]['sf'] = ljug[e]['sf'] + enc.jocs_abc
        ljug[e]['sc'] = ljug[e]['sc'] + enc.jocs_xyz
        if (enc.jocs_abc >= 3):
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pg'] = ljug[e]['pg'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] + 2
        else:
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pp'] = ljug[e]['pp'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] - 1
            
            
        # xyz player
        e = enc.jugador_xyz.jugador  
        if e not in lj:
            # Initialize
            lj.add(e)
            ljug[e] = {}
            ljug[e]['equip'] = enc.jugador_xyz.equipcompeticio.equip.nom
            ljug[e]['equip_id'] = enc.jugador_abc.equipcompeticio.equip.id
            ljug[e]['pj'] = 0
            ljug[e]['pg'] = 0
            ljug[e]['pp'] = 0
            ljug[e]['sf'] = 0
            ljug[e]['sc'] = 0
            ljug[e]['punts'] = 0            
        # Update
        ljug[e]['sf'] = ljug[e]['sf'] + enc.jocs_xyz
        ljug[e]['sc'] = ljug[e]['sc'] + enc.jocs_abc
        if (enc.jocs_abc >= 3):
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pp'] = ljug[e]['pp'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] - 1
        else:
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pg'] = ljug[e]['pg'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] + 2

    # Now we build the classification table. Inverse order
    lojug = ljug.items()
    # Third criteria: sf / sc
    lojug.sort(key=lambda x:-(x[1]['sf']/(x[1]['sc'] + 0.00001)))
    # Second criteria: sf - sc
    lojug.sort(key=lambda x:-(x[1]['sf']-x[1]['sc'])) 
    # First criteria: number of points
    lojug.sort(key=lambda x:-x[1]['punts'])
    # End criteria

    # Build table
    tclass = []
    for e in lojug:
        tclass.append({"id":e[0].id,"equip_id":e[1]["equip_id"],"jugador":e[0].nom,"equip":e[1]['equip'],"pj":e[1]['pj'],"pg":e[1]['pg'],"pp":e[1]['pp'],"sf":e[1]['sf'],"sc":e[1]['sc'],"punts":e[1]['punts']})

    if precalcula:
        # Save into ranquing_calculat table in the mysql database for efficency reasons    
        from django.db import connection,transaction
        cursor = connection.cursor()

        query="DELETE FROM ranquing_calculat WHERE 1=1"
        cursor.execute(query)

        query=''' INSERT INTO ranquing_calculat 
                    (Jugador,Equip,PJ,PG,PP,SF,SC,Punts) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
        queryList = []
        for row in tclass:
            queryList.append([str(row["id"]),str(row["equip_id"]),str(row["pj"]),str(row["pg"]),str(row["pp"]),str(row["sf"]),str(row["sc"]),str(row["punts"])])
        cursor.executemany(query,queryList)
        cursor.close        
        transaction.commit_unless_managed()
        # End save

    else:
        return render_to_response('programa/ranquing.html',
            {'classificacio':tclass},
            context_instance=RequestContext(request))


def ranquing_segona_fase(request,comp_nom,l_comp_12f,l_comp_2punts,l_comp_1punt,l_comp_1_5punts = [], precalcula=False):
    # Scheme similar to the ranquing_primera_fase function        
    # The difference with the ranquing_primera_fase function is that now the same player is two different JugadorEquipCompeticio
    # We must take it into account

    # Get all players that have played at least one match
    lj = set()          # Will be a Jugador set
    ljug= {}
    
    #for p in Individuals.objects.filter(encontre__jornada__competicio__nom = comp_nom):

    # All Individuals (matches)
    enclist = Individuals.objects.filter(
            #encontre__jornada__competicio__nom__in = ['20101fA','20101fB','20102f1','20102f2'])
            encontre__jornada__competicio__nom__in = l_comp_12f)

    for enc in enclist:
        # note: e is a JugadorEquipCompeticio, as we expect
        # abc player
        e = enc.jugador_abc.jugador
        comp_nom = enc.encontre.jornada.competicio.nom    
        if e not in lj:
            # Initialize
            lj.add(e)
            ljug[e] = {}
            ljug[e]['equip'] = enc.jugador_abc.equipcompeticio.equip.nom
            ljug[e]['equip_id'] = enc.jugador_abc.equipcompeticio.equip.id
            ljug[e]['pj'] = 0
            ljug[e]['pg'] = 0
            ljug[e]['pp'] = 0
            ljug[e]['sf'] = 0
            ljug[e]['sc'] = 0
            ljug[e]['punts'] = 0

        # Update
        ljug[e]['sf'] = ljug[e]['sf'] + enc.jocs_abc
        ljug[e]['sc'] = ljug[e]['sc'] + enc.jocs_xyz
        if (enc.jocs_abc >= 3):
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pg'] = ljug[e]['pg'] + 1
            #  Modificacio
            #if enc.encontre.jornada.competicio.nom in ['20101fA','20101fB','20102f1']: 
            if comp_nom in l_comp_2punts:
                ljug[e]['punts'] = ljug[e]['punts'] + 2
            #elif enc.encontre.jornada.competicio.nom in ['20102f2']: 
            elif comp_nom in l_comp_1_5punts:
                ljug[e]['punts'] = ljug[e]['punts'] + 1.5
            elif comp_nom in l_comp_1punt:
                ljug[e]['punts'] = ljug[e]['punts'] + 1
        else:
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pp'] = ljug[e]['pp'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] - 1

            
        # xyz player
        e = enc.jugador_xyz.jugador                
        if e not in lj:
            # Initialize
            lj.add(e)       
            ljug[e] = {}
            ljug[e]['equip'] = enc.jugador_xyz.equipcompeticio.equip.nom
            ljug[e]['equip_id'] = enc.jugador_abc.equipcompeticio.equip.id
            ljug[e]['pj'] = 0
            ljug[e]['pg'] = 0
            ljug[e]['pp'] = 0
            ljug[e]['sf'] = 0
            ljug[e]['sc'] = 0
            ljug[e]['punts'] = 0

        # Update
        ljug[e]['sf'] = ljug[e]['sf'] + enc.jocs_xyz
        ljug[e]['sc'] = ljug[e]['sc'] + enc.jocs_abc
        if (enc.jocs_abc >= 3):
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pp'] = ljug[e]['pp'] + 1
            ljug[e]['punts'] = ljug[e]['punts'] - 1
        else:
            ljug[e]['pj'] = ljug[e]['pj'] + 1
            ljug[e]['pg'] = ljug[e]['pg'] + 1
            # Modificacio
            #if enc.encontre.jornada.competicio.nom in ['20101fA','20101fB','20102f1']: 
            if comp_nom in l_comp_2punts:
                ljug[e]['punts'] = ljug[e]['punts'] + 2
            #elif enc.encontre.jornada.competicio.nom in ['20102f2']:
            elif comp_nom in l_comp_1_5punts: 
                ljug[e]['punts'] = ljug[e]['punts'] + 1.5
            elif comp_nom in l_comp_1punt: 
                ljug[e]['punts'] = ljug[e]['punts'] + 1


    # Now we build the classification table. Inverse order
    lojug = ljug.items()
    # Third criteria: sf / sc
    lojug.sort(key=lambda x:-(x[1]['sf']/(x[1]['sc'] + 0.00001)))
    # Second criteria: sf - sc
    lojug.sort(key=lambda x:-(x[1]['sf']-x[1]['sc'])) 
    # First criteria: number of points
    lojug.sort(key=lambda x:-x[1]['punts'])
    # End criteria

    # Build table
    tclass = []
    for e in lojug:
        tclass.append({"id":e[0].id,"equip_id":e[1]["equip_id"],"jugador":e[0].nom,"equip":e[1]['equip'],"pj":e[1]['pj'],"pg":e[1]['pg'],"pp":e[1]['pp'],"sf":e[1]['sf'],"sc":e[1]['sc'],"punts":e[1]['punts']})

    if precalcula:
        # Save into ranquing_calculat table in the mysql database for efficency reasons    
        from django.db import connection,transaction
        cursor = connection.cursor()

        query="DELETE FROM ranquing_calculat WHERE 1=1"
        cursor.execute(query)

        query=''' INSERT INTO ranquing_calculat 
                    (Jugador,Equip,PJ,PG,PP,SF,SC,Punts) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
        queryList = []
        for row in tclass:
            queryList.append([str(row["id"]),str(row["equip_id"]),str(row["pj"]),str(row["pg"]),
                                str(row["pp"]),str(row["sf"]),str(row["sc"]),str(row["punts"])])
        cursor.executemany(query,queryList)
        cursor.close()
        transaction.commit_unless_managed()
        # End save

    else:
        return render_to_response('programa/ranquing.html',
            {'classificacio':tclass},
            context_instance=RequestContext(request))


def ranquing_precalcula():
    l_comp_12f = ['20121f','20122f1','20122f2','20122f3']
    l_comp_2punts = ['20121f','20122f1']
    l_comp_1_5punts = ['20122f2']
    l_comp_1punt = ['20122f3']
    ranquing_segona_fase('','20122f123',l_comp_12f,l_comp_2punts,l_comp_1punt,l_comp_1_5punts,precalcula=True)       

    
def ranquing_utilitzant_precalcula(request):
    # Query to retrieve ranquing_calculat table with correct jugador and equip names    
    from django.db import connection, transaction
    cursor = connection.cursor()

    query=''' SELECT a.jugador as id, a.equip as equip_id, b.nom, e.nom, a.PJ, a.PG, a.PP, a.SF, a.SC, a.Punts
                FROM ranquing_calculat a
                LEFT JOIN programa_jugador b
                ON a.jugador = CONVERT( b.id, CHAR( 50 ) )
                LEFT JOIN programa_jugadorequipcompeticio c
                ON a.jugador = CONVERT( c.jugador_id, CHAR( 50 ) )
                LEFT JOIN programa_equipcompeticio d
                ON c.equipcompeticio_id = d.id
                LEFT JOIN programa_equip e
                ON d.equip_id = e.id
                LEFT JOIN programa_competicio f
                ON d.competicio_id = f.id
                WHERE f.nom = "20122f1"
                OR f.nom = "20122f2"
                OR f.nom = "20122f3"
                order by a.Punts DESC'''
                
    cursor.execute(query)
    
    tclass = []    
    rows = cursor.fetchall()
    for row in rows:
        tclass.append({"id":row[0], "equip_id":row[1], "jugador":row[2], "equip":row[3], "pj":row[4],
            "pg":row[5], "pp":row[6], "sf":row[7], "sc":row[8], "punts":row[9]})
    
    return render_to_response('programa/ranquing.html',
        {'classificacio':tclass},
        context_instance=RequestContext(request))


def ranquing_precalcula_manual(request):
    ranquing_precalcula()
    return HttpResponseRedirect('http://intercomarcal.alwaysdata.net/programa/index/')


def veure_acta(request,acta_id):   
    enc = Encontre.objects.filter(id=acta_id)[0]
    myform = ActaForm(enc)
    for fieldname in myform.fields:
        myform.fields[fieldname].widget.attrs['readonly'] = True
        #myform.fields[fieldname].widget.attrs['editable'] = False
    return render_to_response('programa/veure_acta.html',
        {'myform':myform,'local':enc.local,'visitant':enc.visitant,'acta_id':acta_id}, 
        context_instance=RequestContext(request))

def veure_acta_cd(request,acta_id):   
    enc = Encontre.objects.filter(id=acta_id)[0]
    myform = ActaFormCD(enc)
    for fieldname in myform.fields:
        myform.fields[fieldname].widget.attrs['readonly'] = True
        #myform.fields[fieldname].widget.attrs['editable'] = False
    return render_to_response('programa/veure_acta_cd.html',
        {'myform':myform,'local':enc.local,'visitant':enc.visitant,'acta_id':acta_id}, 
        context_instance=RequestContext(request))


def login_acta(request,acta_id):
    enc = Encontre.objects.filter(id=acta_id)[0]
    myform = ActaForm(enc)
    myloginform = LoginForm()
    for fieldname in myform.fields:
        myform.fields[fieldname].widget.attrs['readonly'] = True
        #myform.fields[fieldname].widget.attrs['editable'] = False

    if request.method == 'POST':
        myloginform = LoginForm(request.POST)
        if myloginform.is_valid():
            fcd = myloginform.cleaned_data
            user = authenticate(username=fcd["username"], password=fcd["password"])
            if user is None:
                myloginform.errors['username'] = ErrorList(['Identificacio incorrecta'])                         
                response = render_to_response('programa/login_acta.html',
                    {'myform':myform,'local':enc.local,'visitant':enc.visitant,'myloginform':myloginform}, 
                    context_instance=RequestContext(request))
                response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR CNT"' 
                return response
            else:
                # All ok!
                login(request, user)
                return HttpResponseRedirect("/programa/acta/" + str(acta_id) + "/")               
        else:        
            response = render_to_response('programa/login_acta.html',
                {'myform':myform,'local':enc.local,'visitant':enc.visitant,'myloginform':myloginform}, 
                context_instance=RequestContext(request))      
            response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR CNT"'
            return response
    else:        
        myloginform = LoginForm()
        response = render_to_response('programa/login_acta.html',
            {'myform':myform,'local':enc.local,'visitant':enc.visitant,'myloginform':myloginform}, 
            context_instance=RequestContext(request))
        #response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR CNT"'
        return response
        
def acta(request,acta_id):
    enc = Encontre.objects.filter(id=acta_id)[0]
    comp_nom = enc.jornada.competicio.nom

    valid = True
    if not request.user.is_authenticated():
        valid = False
    else:
        if not request.user.is_staff:
            luec = UserEquipCompeticio.objects.filter(user=request.user)
            if luec < 0:
                valid = False
            else:
                uec = luec[0]
                if not (uec.equipcompeticio == enc.local or uec.equipcompeticio == enc.visitant):
                    valid = False
                            
    if not valid:
        return HttpResponseRedirect('/programa/veure_acta/' + str(acta_id) + '/')

    # User is valid
    if request.method == 'POST':
        myform = ActaForm(enc,request.POST)
        if myform.is_valid():
            fcd = myform.cleaned_data
            lresabc = ["abcr1","abcr2","abcr3","abcrd","abcr4","abcr5","abcr6"]
            lresxyz = ["xyzr1","xyzr2","xyzr3","xyzrd","xyzr4","xyzr5","xyzr6"]
            ljugabc = ["abc1","abc2","abc3","abcd1","abcd2","abc4","abc5","abc6"]
            ljugxyz = ["xyz1","xyz2","xyz3","xyzd1","xyzd2","xyz4","xyz5","xyz6"]

            err = False
            # Check that players belong to its teams
            for i in range(0,len(ljugabc)):
                if (fcd[ljugabc[i]].equipcompeticio != fcd["equipabc"]):
                    myform.errors[ljugabc[i]] = ErrorList(["Aquest jugador no pertany a l'equip."])
                    err = True
                if (fcd[ljugxyz[i]].equipcompeticio == fcd["equipabc"]):
                    myform.errors[ljugxyz[i]] = ErrorList(["Aquest jugador no pertany a l'equip."])
                    err = True 
            # Check that one and only one result is 3 in each match
            for i in range(0,len(lresabc)):
                if ((fcd[lresabc[i]] < 3 and fcd[lresxyz[i]] < 3)
                        or (fcd[lresabc[i]] == 3 and fcd[lresxyz[i]] == 3)):
                    myform.errors[lresabc[i]] = ErrorList(["Resultat incorrecte."])
                    err = True
                    
            # Check that there is no repeated match - TBD
            
            if err:
                return render_to_response('programa/acta.html',
                    {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                    context_instance=RequestContext(request))
            
            
            # All ok
            # - Update abc
            enc.abc = fcd["equipabc"]
            # - Update resultats
            [res_abc,jocs_abc] = [0,0]
            for r in lresabc:
                jocs_abc = jocs_abc + fcd[r]
                if fcd[r] == 3:
                    res_abc = res_abc + 1
            [res_xyz,jocs_xyz] = [0,0]
            for r in lresxyz:
                jocs_xyz = jocs_xyz + fcd[r]
                if fcd[r] == 3:
                    res_xyz = res_xyz + 1
            if enc.abc == enc.local:
                [enc.jocs_local,enc.resultat_local] = [jocs_abc,res_abc]
                [enc.jocs_visitant,enc.resultat_visitant] = [jocs_xyz,res_xyz]
            else:
                [enc.jocs_local,enc.resultat_local] = [jocs_xyz,res_xyz]
                [enc.jocs_visitant,enc.resultat_visitant] = [jocs_abc,res_abc]
            enc.save()
            
            # - Create Individuals and Dobles
            for i in range(1,7):
                lind = Individuals.objects.filter(encontre = enc,numero = i)
                if len(lind) > 0:
                    ind = lind[0]
                else:
                    ind = Individuals()
                ind.encontre = enc
                ind.numero = i
                ind.jugador_abc = fcd["abc" + str(i)]
                ind.jugador_xyz = fcd["xyz" + str(i)]
                ind.jocs_abc = fcd["abcr" + str(i)]
                ind.jocs_xyz = fcd["xyzr" + str(i)]
                ind.save()    
            ldob = Dobles.objects.filter(encontre = enc)
            if len(ldob) > 0:
                dob = ldob[0]
            else:
                dob = Dobles()
            dob.encontre = enc
            dob.jugador_abc_1 = fcd["abcd1"]
            dob.jugador_abc_2 = fcd["abcd2"]
            dob.jugador_xyz_1 = fcd["xyzd1"]
            dob.jugador_xyz_2 = fcd["xyzd2"]
            dob.jocs_abc = fcd["abcrd"]
            dob.jocs_xyz = fcd["xyzrd"]
            dob.save()                

            logout(request)
            return HttpResponseRedirect('/programa/calendari/' + str(comp_nom) + '/')
            
        else:
            return render_to_response('programa/acta.html',
                {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                context_instance=RequestContext(request))
    else:
        myform = ActaForm(enc)
        response = render_to_response('programa/acta.html',
                {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                context_instance=RequestContext(request))
        response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
        return response   


def acta_cd(request,acta_id):
    enc = Encontre.objects.filter(id=acta_id)[0]
    comp_nom = enc.jornada.competicio.nom
    
    if request.method == 'POST':
        myform = ActaFormCD(enc,request.POST)
        if myform.is_valid():
            fcd = myform.cleaned_data

            # Validate user
            valid = True
            f_username = fcd["username"]
            f_password = fcd["password"]
            lusers = User.objects.filter(username=f_username)
            if len(lusers) < 1:
                valid = False
                myform.errors['username'] = ErrorList(['Usuari no existent'])
            elif not(lusers[0].check_password(f_password)):
                valid = False
                myform.errors['password'] = ErrorList(['Contrassenya incorrecta'])
            elif not lusers[0].is_staff:
                luec = UserEquipCompeticio.objects.filter(user__username=f_username)
                if len(luec) < 1:
                    valid = False
                else:
                    uec = luec[0]
                    if not (uec.equipcompeticio == enc.local or uec.equipcompeticio == enc.visitant):
                        valid = False
                        myform.errors['username'] = ErrorList(['No pots modificar aquest partit'])
            if not valid:
                response = render_to_response('programa/acta_cd.html',
                        {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                        context_instance=RequestContext(request))
                response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
                return response    
            # End user validation

            lresabc = ["abcr1","abcr2","abcr3","abcrd","abcr4","abcr5","abcr6"]
            lresxyz = ["xyzr1","xyzr2","xyzr3","xyzrd","xyzr4","xyzr5","xyzr6"]
            ljugabc = ["abc1","abc2","abc3","abcd1","abcd2","abc4","abc5","abc6"]
            ljugxyz = ["xyz1","xyz2","xyz3","xyzd1","xyzd2","xyz4","xyz5","xyz6"]

            err = False
            # Check that players belong to its teams
            for i in range(0,len(ljugabc)):
                if (fcd[ljugabc[i]].equipcompeticio != fcd["equipabc"]):
                    myform.errors[ljugabc[i]] = ErrorList(["Aquest jugador no pertany a l'equip."])
                    err = True
                if (fcd[ljugxyz[i]].equipcompeticio == fcd["equipabc"]):
                    myform.errors[ljugxyz[i]] = ErrorList(["Aquest jugador no pertany a l'equip."])
                    err = True 
            # Check that one and only one result is 3 in each match
            for i in range(0,len(lresabc)):
                if ((fcd[lresabc[i]] < 3 and fcd[lresxyz[i]] < 3)
                        or (fcd[lresabc[i]] == 3 and fcd[lresxyz[i]] == 3)):
                    myform.errors[lresabc[i]] = ErrorList(["Resultat incorrecte."])
                    err = True
                    
            # Check that there is no repeated match - TBD
            
            if err:
                response = render_to_response('programa/acta_cd.html',
                    {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                    context_instance=RequestContext(request))
                response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
                return response
            
            # All ok
            # - Update abc
            enc.abc = fcd["equipabc"]
            # - Update resultats
            [res_abc,jocs_abc] = [0,0]
            for r in lresabc:
                jocs_abc = jocs_abc + fcd[r]
                if fcd[r] == 3:
                    res_abc = res_abc + 1
            [res_xyz,jocs_xyz] = [0,0]
            for r in lresxyz:
                jocs_xyz = jocs_xyz + fcd[r]
                if fcd[r] == 3:
                    res_xyz = res_xyz + 1
            if enc.abc == enc.local:
                [enc.jocs_local,enc.resultat_local] = [jocs_abc,res_abc]
                [enc.jocs_visitant,enc.resultat_visitant] = [jocs_xyz,res_xyz]
            else:
                [enc.jocs_local,enc.resultat_local] = [jocs_xyz,res_xyz]
                [enc.jocs_visitant,enc.resultat_visitant] = [jocs_abc,res_abc]
            enc.save()
            
            # - Create Individuals and Dobles
            for i in range(1,7):
                lind = Individuals.objects.filter(encontre = enc,numero = i)
                if len(lind) > 0:
                    ind = lind[0]
                else:
                    ind = Individuals()
                ind.encontre = enc
                ind.numero = i
                ind.jugador_abc = fcd["abc" + str(i)]
                ind.jugador_xyz = fcd["xyz" + str(i)]
                ind.jocs_abc = fcd["abcr" + str(i)]
                ind.jocs_xyz = fcd["xyzr" + str(i)]
                ind.save()    
            ldob = Dobles.objects.filter(encontre = enc)
            if len(ldob) > 0:
                dob = ldob[0]
            else:
                dob = Dobles()
            dob.encontre = enc
            dob.jugador_abc_1 = fcd["abcd1"]
            dob.jugador_abc_2 = fcd["abcd2"]
            dob.jugador_xyz_1 = fcd["xyzd1"]
            dob.jugador_xyz_2 = fcd["xyzd2"]
            dob.jocs_abc = fcd["abcrd"]
            dob.jocs_xyz = fcd["xyzrd"]
            dob.save()                

            #return HttpResponseRedirect('/programa/calendari/' + str(comp_nom) + '/')
            if comp_nom == '20101fA':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-1.html')            
            elif comp_nom == '20101fB':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-2.html')            
            if comp_nom == '20102f1':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-1_05.html')            
            elif comp_nom == '20102f2':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-2_05.html')            

            if comp_nom == '20111f':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga.html')
            elif comp_nom == '20112f1':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga-2011-2012.html')
            elif comp_nom == '20112f2':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga-2011-2012_17.html')

            if comp_nom == '20121f':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga_23.html')
            elif comp_nom == '20122f1':
                ranquing_precalcula()
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga_24.html')
            elif comp_nom == '20122f2':
                ranquing_precalcula()
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga_7268.html')
            elif comp_nom == '20122f3':
                ranquing_precalcula()
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-lliga_3782.html')

            return HttpResponseRedirect('http://ttintercomarcal.blogspot.com')

        else:
            response = render_to_response('programa/acta_cd.html',
                {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                context_instance=RequestContext(request))
            response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
            return response
    else:
        myform = ActaFormCD(enc)
        response = render_to_response('programa/acta_cd.html',
                {'myform':myform,'local':enc.local,'visitant':enc.visitant}, 
                context_instance=RequestContext(request))
        response["P3P"] = 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'
        return response   

def estadistiques(request):
    return render_to_response('programa/estadistiques.html',{},context_instance=RequestContext(request))
