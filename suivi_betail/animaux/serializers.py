from rest_framework import serializers

from .models import Animal, Position, Device, Zone, Alerte


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'nom', 'type_device', 'statut',
            'batterie', 'date_activation', 'date_dernier_contact'
        ]


class PositionSerializer(serializers.ModelSerializer):
    animal_nom = serializers.CharField(source='animal.nom', read_only=True)
    
    class Meta:
        model = Position
        fields = [
            'id', 'animal', 'animal_nom', 'latitude', 'longitude',
            'altitude', 'timestamp', 'batterie', 'satellites',
            'accuracy', 'speed', 'course', 'raw_data', 'format_donnees'
        ]


class AnimalSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    derniere_position = serializers.SerializerMethodField()
    
    class Meta:
        model = Animal
        fields = [
            'id', 'nom', 'type_animal', 'race', 'date_naissance',
            'device', 'device_id', 'statut', 'date_dernier_contact',
            'emoji', 'couleur', 'derniere_position'
        ]
    
    def get_derniere_position(self, obj):
        try:
            derniere = obj.position_set.order_by('-timestamp').first()
            if derniere:
                return {
                    'latitude': float(derniere.latitude),
                    'longitude': float(derniere.longitude),
                    'timestamp': derniere.timestamp.isoformat(),
                    'batterie': derniere.batterie
                }
        except Exception:
            pass
        return None


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = [
            'id', 'nom', 'description', 'type_zone',
            'polygone', 'couleur', 'date_creation'
        ]


class AlerteSerializer(serializers.ModelSerializer):
    animal_nom = serializers.CharField(source='animal.nom', read_only=True)
    
    class Meta:
        model = Alerte
        fields = [
            'id', 'animal', 'animal_nom', 'type_alerte', 'priorite',
            'message', 'position', 'resolue', 'date_creation', 'date_resolution'
        ]


class TBeamDataSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    batterie = serializers.FloatField(required=False, allow_null=True)
    satellites = serializers.IntegerField(required=False, default=0)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    altitude = serializers.FloatField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False)
    speed = serializers.FloatField(required=False, allow_null=True)
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("La latitude doit être entre -90 et 90")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("La longitude doit être entre -180 et 180")
        return value
