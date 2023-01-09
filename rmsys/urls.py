"""rmsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]


# Use include() to add paths from the catalog application
from django.conf.urls import include

urlpatterns += [
    path('risk/', include('risk.urls')),
]


# Add URL maps to redirect the base URL to our application
from django.views.generic import RedirectView

urlpatterns += [
    path('', RedirectView.as_view(url='/risk/slot', permanent=True)),
]

# using django built-in login
from django.contrib.auth import views
from rmsys.form import UserLoginForm
urlpatterns += [
    path('login/',
         views.LoginView.as_view(
             template_name='registration/login.html',
             authentication_form=UserLoginForm
         ),
         name='login'
         )]
urlpatterns += [
    path('logout/',
         views.LogoutView.as_view(),
         name='logout'
         )]

# with django allauth
urlpatterns += [
    path('allauth/', include('allauth.urls')),
]

# add api urls
urlpatterns += [
    path('api/', include('api.urls')),
]

# add ws urls
urlpatterns += [
    path('ws/', include('ws.urls')),
]

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

import debug_toolbar

urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
]
