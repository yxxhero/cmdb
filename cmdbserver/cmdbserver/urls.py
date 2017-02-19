"""cmdbserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url,include
from django.contrib import admin
from server.views import index,login,register,signin,logout,posthostinfo,deletehost,saltadmin,saltcontrol,showcmdhistory,filterhistory,saltconfig,codepublish,commitupdate
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',index),
    url(r'^login/',login),
    url(r'^index/', index),
    url(r'^register/',register),
    url(r'^signin/',signin),
    url(r'^logout/',logout),
    url(r'^posthostinfo/',posthostinfo),
    url(r'^deletehost/',deletehost),
    url(r'^saltadmin/',saltadmin),
    url(r'^saltcmdrun/',saltcontrol),
    url(r'^salthistory/',showcmdhistory),
    url(r'^historybytime/',filterhistory),
    url(r'^saltconfigview/',saltconfig),
    url(r'^codepublish/',codepublish),
    url(r'^putcodecommit/',commitupdate),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
