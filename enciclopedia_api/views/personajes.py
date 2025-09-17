# enciclopedia_api/views/personajes.py

from rest_framework import viewsets, permissions, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters import rest_framework as df

from enciclopedia_api.models import Personaje
from enciclopedia_api.serializers import PersonajeSerializer


class PersonajeFilter(df.FilterSet):
    # Filtros numéricos por rango
    base_ki_min = df.NumberFilter(field_name="base_ki", lookup_expr="gte")
    base_ki_max = df.NumberFilter(field_name="base_ki", lookup_expr="lte")
    total_ki_min = df.NumberFilter(field_name="total_ki", lookup_expr="gte")
    total_ki_max = df.NumberFilter(field_name="total_ki", lookup_expr="lte")

    # Filtros de texto (case-insensitive)
    nombre = df.CharFilter(field_name="nombre", lookup_expr="icontains")
    especie = df.CharFilter(field_name="especie", lookup_expr="icontains")
    genero = df.CharFilter(field_name="genero", lookup_expr="icontains")
    afiliacion = df.CharFilter(field_name="afiliacion", lookup_expr="icontains")

    class Meta:
        model = Personaje
        fields = [
            "nombre", "especie", "genero", "afiliacion",
            "base_ki_min", "base_ki_max", "total_ki_min", "total_ki_max"
        ]


class PersonajeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Personaje. Permite listar, crear, actualizar, eliminar personajes,
    comparar dos personajes y obtener estadísticas agrupadas por afiliación.
    """
    queryset = Personaje.objects.all().order_by("nombre")
    serializer_class = PersonajeSerializer
    permission_classes = [permissions.AllowAny]  # Cambia esto si luego activas autenticación

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # Búsqueda y ordenamiento
    filter_backends = [df.DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PersonajeFilter
    search_fields = ["nombre", "especie", "afiliacion", "descripcion"]
    ordering_fields = ["nombre", "base_ki", "total_ki"]
    ordering = ["nombre"]

    @action(detail=False, methods=["get"], url_path="comparar")
    def comparar(self, request):
        """
        Comparar 2 personajes:
        - /api/personajes/comparar/?ids=1,2
        - o /api/personajes/comparar/?a=1&b=2
        Devuelve ambos registros + deltas de base_ki y total_ki.
        """
        ids_param = request.query_params.get("ids")
        a = request.query_params.get("a")
        b = request.query_params.get("b")

        ids = []
        if ids_param:
            parts = [p.strip() for p in ids_param.split(",") if p.strip()]
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                ids = [int(parts[0]), int(parts[1])]
        elif a and b and a.isdigit() and b.isdigit():
            ids = [int(a), int(b)]

        if len(ids) != 2:
            return Response({"detail": "Debes enviar dos IDs: ?ids=1,2 o ?a=1&b=2"}, status=400)

        qs = list(Personaje.objects.filter(id__in=ids))
        if len(qs) != 2:
            return Response({"detail": "No se encontraron ambos personajes."}, status=404)

        data = PersonajeSerializer(qs, many=True, context={"request": request}).data
        data.sort(key=lambda x: x["id"])

        base_ki_delta = data[1]["base_ki"] - data[0]["base_ki"]
        total_ki_delta = data[1]["total_ki"] - data[0]["total_ki"]

        return Response({
            "personajes": data,
            "comparacion": {
                "id_a": data[0]["id"],
                "id_b": data[1]["id"],
                "base_ki_delta": base_ki_delta,
                "total_ki_delta": total_ki_delta
            }
        })

    @action(detail=False, methods=["get"], url_path="estadisticas")
    def estadisticas(self, request):
        """
        Agrupa por afiliación y devuelve nombre, KI y la imagen absoluta.
        """
        grupos = {}

        # Ajusta 'imagen' si tu ImageField se llama diferente
        qs = Personaje.objects.all().only(
            "id", "nombre", "base_ki", "total_ki", "afiliacion", "imagen"
        )

        for pj in qs:
            afiliacion = pj.afiliacion or "Sin afiliación"

            # Construir URL absoluta de la imagen (o None si no hay)
            img_url = None
            try:
                if getattr(pj, "imagen", None):
                    # ejemplo: http://localhost:8000/media/...
                    img_url = request.build_absolute_uri(pj.imagen.url)
            except Exception:
                img_url = None

            grupos.setdefault(afiliacion, []).append({
                "id": pj.id,
                "nombre": pj.nombre,
                "base_ki": pj.base_ki,
                "total_ki": pj.total_ki,
                "imagen_src": img_url,   # <── clave que usa el front
            })

        return Response(grupos)