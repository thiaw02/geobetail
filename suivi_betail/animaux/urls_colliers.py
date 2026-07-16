from django.urls import path
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from . import views_colliers

app_name = 'colliers'

urlpatterns = [
    path('appairer/', views_colliers.appairer_collier, name='appairer'),
    path('appairer-qr/', views_colliers.appairer_collier_qr, name='appairer_qr'),
    path('mes-colliers/', views_colliers.mes_colliers, name='mes_colliers'),
    path('<int:device_id>/dissocier/', views_colliers.dissocier_collier, name='dissocier'),
    path('<int:device_id>/qr-code/', views_colliers.qr_code_collier, name='qr_code'),
]
