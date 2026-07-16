from django.urls import path
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from . import views

app_name = 'colliers'

urlpatterns = [
    # Appairage par code
    path('appairer/', views.appairer_collier, name='appairer'),
    
    # Appairage par QR code (décodé côté client)
    path('appairer-qr/', views.appairer_collier_qr, name='appairer_qr'),
    
    # Liste des colliers de l'utilisateur
    path('mes-colliers/', views.mes_colliers, name='mes_colliers'),
    
    # Dissocier un collier
    path('<int:device_id>/dissocier/', views.dissocier_collier, name='dissocier'),
    
    # Génération QR code
    path('<int:device_id>/qr-code/', views.qr_code_collier, name='qr_code'),
]
