from django.contrib import admin
from .models import Profiles, Personaje

@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Personaje)
class PersonajeAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "especie", "genero", "base_ki", "total_ki", "afiliacion")
    list_filter = ("especie", "genero", "afiliacion")
    search_fields = ("nombre", "especie", "afiliacion")
    ordering = ("nombre",)
