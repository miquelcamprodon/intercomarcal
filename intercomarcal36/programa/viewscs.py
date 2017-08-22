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

def calendari(request,comp_nom):
    listj = Jornada.objects.filter(competicio__nom = comp_nom).order_by("numero")
    lcomp = Competicio.objects.filter(nom = comp_nom)
    if len(lcomp) > 0:
        comp = lcomp[0]
    else:
        comp = "Competicio no existent"
    return render_to_response('programa/calendari.html',
        {'competicio':comp,'jornades':listj},
        context_instance=RequestContext(request)) 


def calendari_entrar(request,comp_nom):
    listj = Jornada.objects.filter(competicio__nom = comp_nom).order_by("numero")
    lcomp = Competicio.objects.filter(nom = comp_nom)
    if len(lcomp) > 0:
        comp = lcomp[0]
    else:
        comp = "Competicio no existent"
    return render_to_response('programa/calendari_entrar.html',
        {'competicio':comp,'jornades':listj},
        context_instance=RequestContext(request))
        
def classificacio(request,comp_nom):  
    equips = EquipCompeticio.objects.filter(competicio__nom = comp_nom)
    
    if comp_nom == "20101fA" or comp_nom == "20101fB":
        [pj,pg,pp,sf,sc,punts] = [{},{},{},{},{},{}]
        # Encontres of the competition
        enccomp = Encontre.objects.filter(jornada__competicio__nom = comp_nom).order_by("jornada__numero")
        for e in equips:
            [pj[e],pg[e],pp[e],sf[e],sc[e],punts[e]] = [0,0,0,0,0,0]
            # Local games
            enclist = enccomp.filter(local=e)
            for enc in enclist:
                if enc.jocs_local != None:
                    [sf[e],sc[e]] = [sf[e]+enc.jocs_local,sc[e]+enc.jocs_visitant]
                    if (enc.resultat_local >= 4):
                        [pj[e],pg[e],punts[e]] = [pj[e] + 1,pg[e] + 1,punts[e] + 2]
                    else:
                        [pj[e],pp[e],punts[e]] = [pj[e] + 1,pp[e] + 1,punts[e] - 0]
            # Visitor games
            enclist = Encontre.objects.filter(visitant=e)
            for enc in enclist:
                if enc.jocs_local != None:
                    [sf[e],sc[e]] = [sf[e]+enc.jocs_visitant,sc[e]+enc.jocs_local]
                    if (enc.resultat_local >= 4):
                        [pj[e],pp[e],punts[e]] = [pj[e] + 1,pp[e] + 1,punts[e] - 0]
                    else:
                        [pj[e],pg[e],punts[e]] = [pj[e] + 1,pg[e] + 1,punts[e] + 2]

        # Now we build the classification table.
        # First criteria: number of points
        loteams = punts.items()
        loteams.sort(key=lambda x:-x[1])
        # End criteria
        print loteams
        # Second criteria: sf - sc
        

        # Third criteria: sf / sc

        # Build table
        tclass = []
        for (e,p) in loteams:
            tclass.append({"equipcompeticio":e,"pj":pj[e],"pg":pg[e],"pp":pp[e],"sf":sf[e],"sc":sc[e],"punts":punts[e]})

        return render_to_response('programa/classificacio.html',
            {'classificacio':tclass},
            context_instance=RequestContext(request))
        
def ranquing(request,comp_nom):
    # If comp_nom == '20101fAB' then we want to show matches
    # in competitions '20101fA' or '20101fB'
        
    if comp_nom == '20101fAB':
        # Get all players that have played at least one match
        lj = []
        #for p in Individuals.objects.filter(encontre__jornada__competicio__nom = comp_nom):
        for p in Individuals.objects.filter(encontre__jornada__competicio__nom__in = ['20101fA','20101fB']):
            lj.append(p.jugador_abc)
            lj.append(p.jugador_xyz)
        lj = set(lj)
    
        [pj,pg,pp,sf,sc,punts] = [{},{},{},{},{},{}]   
        for e in lj:
            [pj[e],pg[e],pp[e],sf[e],sc[e],punts[e]] = [0,0,0,0,0,0]
            # ABC games
            enclist = Individuals.objects.filter(jugador_abc=e)
            for enc in enclist:
                [sf[e],sc[e]] = [sf[e]+enc.jocs_abc,sc[e]+enc.jocs_xyz]
                if (enc.jocs_abc >= 3):
                    [pj[e],pg[e],punts[e]] = [pj[e] + 1,pg[e] + 1,punts[e] + 2]
                else:
                    [pj[e],pp[e],punts[e]] = [pj[e] + 1,pp[e] + 1,punts[e] - 1]
            # XYZ games
            enclist = Individuals.objects.filter(jugador_xyz=e)
            for enc in enclist:
                [sf[e],sc[e]] = [sf[e]+enc.jocs_xyz,sc[e]+enc.jocs_abc]
                if (enc.jocs_abc >= 3):
                    [pj[e],pp[e],punts[e]] = [pj[e] + 1,pp[e] + 1,punts[e] - 1]
                else:
                    [pj[e],pg[e],punts[e]] = [pj[e] + 1,pg[e] + 1,punts[e] + 2]

        # Now we build the classification table.
        # First criteria: number of points
        loteams = punts.items()
        loteams.sort(key=lambda x:-x[1])
        # End criteria

        # Build table
        tclass = []
        for (e,p) in loteams:
            tclass.append({"jugadorec":e,"pj":pj[e],"pg":pg[e],"pp":pp[e],"sf":sf[e],"sc":sc[e],"punts":punts[e]})

        return render_to_response('programa/ranquing.html',
            {'classificacio':tclass},
            context_instance=RequestContext(request))


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
    myform = ActaForm(enc)
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
    compnom = enc.jornada.competicio.nom

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
            return HttpResponseRedirect('/programa/calendari/' + str(compnom) + '/')
            
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
    compnom = enc.jornada.competicio.nom
    
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

            #return HttpResponseRedirect('/programa/calendari/' + str(compnom) + '/')
            if compnom == '20101fA':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-1.html')            
            elif compnom == '20101fB':
                return HttpResponseRedirect('http://ttintercomarcal.blogspot.com/p/calendari-i-resultats-grup-2.html')            


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

