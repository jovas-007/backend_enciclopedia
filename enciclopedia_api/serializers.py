from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profiles, Personaje

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")

class ProfilesSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profiles
        fields = "__all__"

class PersonajeSerializer(serializers.ModelSerializer):
    imagen_src = serializers.SerializerMethodField()

    class Meta:
        model = Personaje
        fields = "__all__"  # incluye imagen, imagen_url, descripcion, y el resto

    def get_imagen_src(self, obj):
        request = self.context.get("request")
        url = None
        if obj.imagen:
            url = obj.imagen.url
        elif obj.imagen_url:
            url = obj.imagen_url
        if url and request is not None:
            return request.build_absolute_uri(url)
        return url
        # Ahora imagen_src siempre tendrá la URL absoluta correcta o None