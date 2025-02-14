from rest_framework import viewsets, status, permissions # Importe 'permissions'
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny #
from .models import Weather_Station, Day, Measurement
from .serializers import WeatherStationSerializer, DaySerializer, MeasurementSerializer
from django.http import HttpResponse
import os


class TestViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list(self, request):
        if request.user.is_authenticated:
            return Response({"message": "LabPenso Rest online! 😉 Você está autenticado 🔓"})
        else:
            return Response({"message": "LabPenso Rest online! 😉 Você não está autenticado 🔒"})

class WeatherStationViewSet(viewsets.ModelViewSet):
    queryset = Weather_Station.objects.all()
    serializer_class = WeatherStationSerializer
    # Alteração aqui: Use IsAuthenticatedOrReadOnly
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    # Alteração aqui: Use IsAuthenticatedOrReadOnly
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Método CREATE SIMPLIFICADO!
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def api_documentation_view(request):
    """
    View para servir a página HTML de documentação da API.
    """
    static_file_path = os.path.join(os.path.dirname(__file__), 'static', 'api', 'documentacao.html') 

    try:
        with open(static_file_path, 'r') as f:
            html_content = f.read()
        return HttpResponse(html_content)
    except FileNotFoundError:
        return HttpResponse("Documentação da API não encontrada.", status=404)
