"""intercomarcal36 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from intercomarcal36.programa import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    # Static files: CSS, images,...
    #url(r'^site_media/(?P<path>.*)$', django.views.static.serve, {'document_root': 'files_media/'}),
    
    url(r'^programa/calendari/(?P<comp_nom>[a-z,A-Z,0-9]+)/',   views.calendari), 
    url(r'^programa/calendari_entrar/(?P<comp_nom>[a-z,A-Z,0-9]+)/',views.calendari_entrar),
    url(r'^programa/classificacio/(?P<comp_nom>[a-z,A-Z,0-9]+)/',views.classificacio),
    url(r'^programa/ranquing/(?P<comp_nom>[a-z,A-Z,0-9]+)/',    views.ranquing),
    url(r'^programa/veure_acta/(?P<acta_id>\d+)/',              views.veure_acta),
    url(r'^programa/veure_acta_cd/(?P<acta_id>\d+)/',           views.veure_acta_cd),
    url(r'^programa/acta/(?P<acta_id>\d+)/',                    views.acta),
    url(r'^programa/acta_cd/(?P<acta_id>\d+)/',                 views.acta_cd),
    url(r'^programa/login_acta/(?P<acta_id>\d+)/',              views.login_acta),
    url(r'^programa/estadistiques/',                            views.estadistiques),
    url(r'^programa/ranquing_precalcula_manual/',               views.ranquing_precalcula_manual),
    url(r'^programa/ranquingtti/',                              views.ranquingtti),    
    url(r'^programa/index/',                                    views.index),
    url(r'^programa/carregarfitxer/',                           views.carregarfitxer),  
    
]
