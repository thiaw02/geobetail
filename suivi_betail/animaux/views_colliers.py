import secrets
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Animal, Device, Position, Zone
from .serializers import DeviceSerializer
from .qr_utils import generer_qr_code, sauvegarder_qr_code


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([AnonRateThrottle])
def appairer_collier(request):
    """
    Appaire un collier à un utilisateur par code d'appairage.
    Accessible sans authentification car c'est la première étape de l'onboarding.
    """
    code = request.data.get('code', '').strip().upper()
    
    if not code:
        return Response({
            'status': 'error',
            'message': 'Le code d\'appairage est requis'
        }, status=400)
    
    device = get_object_or_404(Device, code_appairage=code)
    
    if device.est_appaire:
        return Response({
            'status': 'error',
            'message': 'Ce collier est déjà associé à un compte'
        }, status=409)
    
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    
    user = None
    if username and password:
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({
                'status': 'error',
                'message': 'Identifiants incorrects'
            }, status=401)
    else:
        email = request.data.get('email', '').strip()
        if not email:
            return Response({
                'status': 'error',
                'message': 'Email ou identifiants requis'
            }, status=400)
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
            }
        )
        if created:
            temp_password = secrets.token_urlsafe(12)
            user.set_password(temp_password)
            user.save()
    
    device.proprietaire = user
    device.est_appaire = True
    device.date_appairage = timezone.now()
    device.save()
    
    sauvegarder_qr_code(device)
    
    return Response({
        'status': 'success',
        'message': f'Collier {device.code_appairage} appairé avec succès',
        'device': DeviceSerializer(device).data,
        'user_created': user is not None and not user.is_authenticated
    }, status=201)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([AnonRateThrottle])
def appairer_collier_qr(request):
    """
    Appaire un collier à partir d'un QR code scanné.
    Le QR code contient le code d'appairage.
    """
    qr_data = request.data.get('qr_data', '').strip()
    
    if not qr_data:
        return Response({
            'status': 'error',
            'message': 'Données QR code manquantes'
        }, status=400)
    
    code = qr_data.replace('geobetail://pair/', '').strip().upper()
    
    if not code:
        return Response({
            'status': 'error',
            'message': 'QR code invalide'
        }, status=400)
    
    device = get_object_or_404(Device, code_appairage=code)
    
    if device.est_appaire:
        return Response({
            'status': 'error',
            'message': 'Ce collier est déjà associé à un compte'
        }, status=409)
    
    request.data['code'] = code
    return appairer_collier(request)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def mes_colliers(request):
    """
    Liste des colliers de l'utilisateur connecté.
    """
    devices = Device.objects.filter(proprietaire=request.user)
    
    data = []
    for device in devices:
        animal = Animal.objects.filter(device=device).first()
        derniere_position = Position.objects.filter(
            animal=animal
        ).order_by('-timestamp').first() if animal else None
        
        data.append({
            'id': device.id,
            'device_id': device.device_id,
            'nom': device.nom,
            'type_device': device.type_device,
            'statut': device.statut,
            'batterie': device.batterie,
            'code_appairage': device.code_appairage,
            'est_appaire': device.est_appaire,
            'date_appairage': device.date_appairage.isoformat() if device.date_appairage else None,
            'date_dernier_contact': device.date_dernier_contact.isoformat() if device.date_dernier_contact else None,
            'animal': {
                'id': animal.id,
                'nom': animal.nom,
                'type_animal': animal.type_animal,
                'statut': animal.statut,
            } if animal else None,
            'derniere_position': {
                'latitude': float(derniere_position.latitude),
                'longitude': float(derniere_position.longitude),
                'timestamp': derniere_position.timestamp.isoformat(),
                'batterie': derniere_position.batterie
            } if derniere_position else None
        })
    
    return Response({
        'status': 'success',
        'count': len(data),
        'colliers': data
    })


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def dissocier_collier(request, device_id):
    """
    Dissocie un collier de l'utilisateur.
    """
    device = get_object_or_404(Device, id=device_id, proprietaire=request.user)
    
    animal = Animal.objects.filter(device=device).first()
    if animal:
        animal.device = None
        animal.save()
    
    device.proprietaire = None
    device.est_appaire = False
    device.date_appairage = None
    device.save()
    
    return Response({
        'status': 'success',
        'message': f'Collier {device.code_appairage} dissocié avec succès'
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def qr_code_collier(request, device_id):
    """
    Génère le QR code d'un collier.
    """
    device = get_object_or_404(Device, id=device_id, proprietaire=request.user)
    
    qr_data = generer_qr_code(device)
    if not qr_data:
        return Response({
            'status': 'error',
            'message': 'Code d\'appairage manquant'
        }, status=400)
    
    from django.http import HttpResponse
    return HttpResponse(qr_data, content_type='image/png')
