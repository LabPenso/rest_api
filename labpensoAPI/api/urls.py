from django.urls import path, include
from rest_framework import routers
from django.urls import path
from .views import WeatherStationViewSet, DayViewSet, MeasurementViewSet, TestViewSet, api_documentation_view 

router = routers.DefaultRouter()
router.register(r'stations', WeatherStationViewSet, basename='station')
router.register(r'days', DayViewSet, basename='day')
router.register(r'measurements', MeasurementViewSet, basename='measurement')
router.register(r'test', TestViewSet, basename='test')

urlpatterns = [
    path('', api_documentation_view, name='api-docs'), 
    path('', include(router.urls)), 
] 