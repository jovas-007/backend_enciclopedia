from rest_framework import serializers
from rest_framework.authtoken.models import Token
from enciclopedia_api.models import *

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
    class Meta:
        model = Personaje
        fields = "__all__"
