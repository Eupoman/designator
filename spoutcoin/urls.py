"""spoutcoin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from persona.views import AuthenticationUserView, ActivationView, LoginView, process_order, ajax_send_pin,\
    TrainingDataView

from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^training/',TrainingDataView.as_view(), name='training'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^signup/$', AuthenticationUserView.as_view(), name='signup'),
    url(r'^$', AuthenticationUserView.as_view(), name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ActivationView.as_view(), name='activate'),
    url(r'^logout/$', auth_views.logout,{'next_page': '/'}, name='logout'),
    url(r'^login/$', LoginView.as_view(), name='login_validate'),
    url(r'^send_otp/$', process_order, name='send_otp'),
    url(r'^ajax_send_pin/$', ajax_send_pin, name='ajax_send_pin'),
    url(r'^profile/$', login_required(TemplateView.as_view(template_name="home.html")), name='add-muusic'),
    url(r'^error/$', TemplateView.as_view(template_name="error.html"), name='add-muusic'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)