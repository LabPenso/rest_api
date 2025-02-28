from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Weather_Station, Day, Measurement
from .serializers import WeatherStationSerializer, DaySerializer, MeasurementSerializer
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.http import HttpResponse
import os

class TestViewSet(viewsets.ViewSet):
    """
    retorna mensagem de status da API e do usuário.
    """
    permission_classes = [AllowAny]
    def list(self, request):
        if request.user.is_authenticated:
            return Response({"message": "LabPenso Rest online! 😉 You're authenticated 🔓"})
        else:
            return Response({"message": "LabPenso Rest online! 😉 You're not authenticadted 🔒"})

def api_documentation_view(request):
    """
    retorna pagina de documentacao
    """
    static_file_path = os.path.join(os.path.dirname(__file__), 'static', 'documentacao.html')

    try:
        with open(static_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html; charset=utf-8')
    except FileNotFoundError:
        return HttpResponse("Documentation page not found", status=404)

class WeatherStationViewSet(viewsets.ModelViewSet):
    queryset = Weather_Station.objects.all()
    serializer_class = WeatherStationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response({"message": "Estação deletada", "data": serializer.data}, status=status.HTTP_200_OK)

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response({"message": "deleted Day.", "data": serializer.data}, status=status.HTTP_200_OK)

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response({"message": "Measurement deleted.", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='station/(?P<station_id>\\d+)')
    def by_station(self, request, station_id=None):
        if not Weather_Station.objects.filter(id=station_id).exists():
            return Response({"error": "Station not found"}, status=status.HTTP_404_NOT_FOUND)

        measurements = Measurement.objects.filter(Weather_Station__id=station_id)
        serializer = self.get_serializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='day/(?P<day>\\d{4}-\\d{2}-\\d{2})')
    def by_day(self, request, day=None):
        if not Day.objects.filter(data=day).exists():
            return Response({"error": "No data was found for the given day."}, status=status.HTTP_404_NOT_FOUND)

        measurements = Measurement.objects.filter(Day__data=day)
        serializer = self.get_serializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='station/(?P<station_id>\\d+)/day/(?P<day>\\d{4}-\\d{2}-\\d{2})')
    def by_station_and_day(self, request, station_id=None, day=None):
        if not Weather_Station.objects.filter(id=station_id).exists():
            return Response({"error": "Station not found."}, status=status.HTTP_404_NOT_FOUND)

        if not Day.objects.filter(data=day).exists():
            return Response({"error": "No data was found for the given day."}, status=status.HTTP_404_NOT_FOUND)

        measurements = Measurement.objects.filter(Weather_Station__id=station_id, Day__data=day)
        serializer = self.get_serializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='station/(?P<station_id>\\d+)/dates')
    def by_station_and_date_range(self, request, station_id=None):
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        if not Weather_Station.objects.filter(id=station_id).exists():
            return Response({"error": "Station not found."}, status=status.HTTP_404_NOT_FOUND)

        if not start_date or not end_date:
            return Response({"error": "Parameters 'start' and 'end' are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        measurements = Measurement.objects.filter(
            Weather_Station__id=station_id,
            Day__data__range=[start_date, end_date]
        )
        serializer = self.get_serializer(measurements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='station/(?P<station_id>\\d+)/hours')
    def by_station_and_hour_range(self, request, station_id=None):
        start_time = request.query_params.get('start')
        end_time = request.query_params.get('end')

        if not Weather_Station.objects.filter(id=station_id).exists():
            return Response({"error": "Station not found."}, status=status.HTTP_404_NOT_FOUND)

        if not start_time or not end_time:
            return Response({"error": "Parameters 'start' and 'end' are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_datetime = parse_datetime(start_time)
            end_datetime = parse_datetime(end_time)
        except ValueError:
            return Response({"error": "Invalid date format, use ISO 8601 only."}, status=status.HTTP_400_BAD_REQUEST)

        measurements = Measurement.objects.filter(
            Weather_Station__id=station_id,
            timestamp__range=[start_datetime, end_datetime]
        )
        serializer = self.get_serializer(measurements, many=True)
        return Response(serializer.data)
