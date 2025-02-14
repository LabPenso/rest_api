from django.db import models

class Weather_Station(models.Model):
    # station_id REMOVIDO
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

class Day(models.Model):
    data = models.DateField(unique=True)
    observacao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.data)

class Measurement(models.Model):
    Weather_Station = models.ForeignKey(Weather_Station, on_delete=models.CASCADE)
    Day = models.ForeignKey(Day, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    temperature = models.FloatField(blank=True, null=True)
    humidity = models.FloatField(blank=True, null=True)
    uv_index = models.IntegerField(blank=True, null=True)
    pressure = models.FloatField(blank=True, null=True)
    light_intensity = models.IntegerField(blank=True, null=True)
    rain_mm = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('Weather_Station', 'Day', 'timestamp')
    
    def __str__(self):
        return f"{self.Weather_Station} - {self.Day} - {self.timestamp}"