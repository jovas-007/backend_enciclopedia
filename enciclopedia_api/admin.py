from django.contrib import admin
from django.utils.html import format_html
from .models import Profiles, Personaje

@admin.register(Profiles)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Personaje)
class PersonajeAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "especie", "genero", "base_ki", "total_ki", "afiliacion", "miniatura")
    list_filter = ("especie", "genero", "afiliacion")
    search_fields = ("nombre", "especie", "afiliacion", "descripcion")
    ordering = ("nombre",)

    def miniatura(self, obj):
        url = obj.imagen.url if obj.imagen else obj.imagen_url
        if url:
            return format_html('<img src="{}" style="height:40px;"/>', url)
        return "-"
    miniatura.short_description = "Imagen"
