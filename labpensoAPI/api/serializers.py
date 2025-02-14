# serializers.py
from rest_framework import serializers
from .models import Weather_Station, Day, Measurement

class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather_Station
        fields = ['id', 'name', 'latitude', 'longitude','description']

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = '__all__'

class MeasurementSerializer(serializers.ModelSerializer):
    station_id = serializers.IntegerField(write_only=True)  #

    class Meta:
        model = Measurement
        fields = ['station_id', 'timestamp', 'temperature', 'humidity', 'uv_index', 'pressure', 'light_intensity', 'rain_mm']
    
    def create(self, validated_data):
        weather_station_id = validated_data.pop('station_id')  
        weather_station = Weather_Station.objects.get(pk=weather_station_id) 

        day_date = validated_data['timestamp'].date()  
        day, _ = Day.objects.get_or_create(data=day_date)  

        measurement = Measurement.objects.create(
            Weather_Station=weather_station,
            Day=day,
            **validated_data
        )
        return measurement


