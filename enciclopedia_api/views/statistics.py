# enciclopedia_api/views/statistics.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from enciclopedia_api.models import Personaje

class StatisticsViewSet(viewsets.ViewSet):
    """
    ViewSet para devolver estadísticas básicas del dashboard.
    Por ahora solo cuenta personajes; el resto (transformaciones, sagas y episodios)
    se dejan en cero hasta tener modelos correspondientes.
    """

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        # Número de personajes en la BD
        characters_count = Personaje.objects.count()
        # Si en un futuro tienes modelos de transformaciones, sagas, episodios, cámbialos aquí
        stats = {
            "characters": characters_count,
            "transformations": 0,
            "sagas": 0,
            "episodes": 0,
        }
        return Response(stats)
