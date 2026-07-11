from rest_framework import serializers

from .models import Animal, GPSData, TBeamDevice


class GPSDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    animal_id = serializers.CharField(source='device.animal.animal_id', read_only=True, allow_null=True)
    
    class Meta:
        model = GPSData
        fields = [
            'id', 'device_id', 'animal_id', 'latitude', 'longitude',
            'timestamp', 'accuracy', 'satellites', 'altitude',
            'batterie_level', 'vitesse', 'date_reception'
        ]

class TBeamDataSerializer(serializers.Serializer):
    # Données reçues du T-Beam
    device_id = serializers.CharField(max_length=50)
    animal_id = serializers.CharField(max_length=50, required=False, allow_null=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    battery_level = serializers.FloatField(required=False, allow_null=True)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    satellites = serializers.IntegerField(required=False, default=0)
    altitude = serializers.FloatField(required=False, allow_null=True)
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("La latitude doit être entre -90 et 90")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("La longitude doit être entre -180 et 180")
        return value

class AnimalSerializer(serializers.ModelSerializer):
    derniere_position = serializers.SerializerMethodField()
    device_id = serializers.CharField(source='tbeamdevice.device_id', read_only=True, allow_null=True)
    statut_device = serializers.CharField(source='tbeamdevice.statut', read_only=True, allow_null=True)
    
    class Meta:
        model = Animal
        fields = [
            'animal_id', 'name', 'espece', 'statut', 
            'device_id', 'statut_device', 'derniere_position'
        ]
    
    def get_derniere_position(self, obj):
        try:
            derniere_data = GPSData.objects.filter(
                device__animal=obj
            ).order_by('-timestamp').first()
            if derniere_data:
                return {
                    'latitude': float(derniere_data.latitude),
                    'longitude': float(derniere_data.longitude),
                    'timestamp': derniere_data.timestamp,
                    'batterie': derniere_data.batterie_level
                }
        except:
            pass
        return None        