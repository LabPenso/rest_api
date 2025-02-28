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
    station_id = serializers.IntegerField(write_only=True)
    weather_station_id = serializers.IntegerField(source='Weather_Station.id', read_only=True)
    day_id = serializers.IntegerField(source='Day.id', read_only=True)

    class Meta:
        model = Measurement
        fields = ['id', 'station_id', 'day_id', 'weather_station_id', 'timestamp', 'temperature', 'humidity', 'uv_index', 'pressure', 'light_intensity', 'rain_mm']

    def create(self, validated_data):
        station_id = validated_data.pop('station_id')
        print(f"station_id: {station_id}")
        try:
            weather_station = Weather_Station.objects.get(pk=station_id)
        except Weather_Station.DoesNotExist:
            raise serializers.ValidationError({"station_id": f"No Station found with id {station_id}."})

        day_date = validated_data['timestamp'].date()
        day, _ = Day.objects.get_or_create(data=day_date)

        measurement = Measurement.objects.create(
            Weather_Station=weather_station,
            Day=day,
            **validated_data
        )
        return measurement


