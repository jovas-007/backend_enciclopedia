"""point_experts_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from enciclopedia_api.views import bootstrap
from enciclopedia_api.views import users
from enciclopedia_api.views import auth


from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from enciclopedia_api.views.personajes import PersonajeViewSet


from django.conf import settings
from django.conf.urls.static import static

from enciclopedia_api.views.statistics import StatisticsViewSet

router = DefaultRouter()
router.register(r"personajes", PersonajeViewSet, basename="personajes")
router.register(r"statistics", StatisticsViewSet, basename="statistics")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)