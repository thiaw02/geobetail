from django.urls import path
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from . import views

app_name = 'animaux_api'

urlpatterns = [
    # Authentification
    path('token/', views.obtain_token_pair, name='token_obtain_pair'),
    path('token/refresh/', views.refresh_token, name='token_refresh'),
    
    # Données principales
    path('animaux/', views.get_animaux_list, name='animaux_list'),
    path('animaux/actifs/', views.get_active_animals, name='active_animals'),
    path('positions/', views.get_recent_positions, name='recent_positions'),
    path('positions/recentes/', views.get_recent_positions, name='recent_positions_fr'),
    path('dashboard/stats/', views.get_dashboard_stats, name='dashboard_stats'),
    path('zones/', views.get_zones, name='zones'),
    path('alertes/', views.get_alertes, name='alertes'),
    path('devices/', views.get_devices, name='devices'),
    
    # Ingestion T-Beam (protégée)
    path('tbeam/stream/', views.receive_tbeam_data, name='receive_tbeam_data'),
    path('tbeam/latest/', views.get_recent_positions, name='tbeam_latest'),
    
    # Vidéo
    path('upload_image/', views.upload_image, name='upload_image'),
    path('video_stream/', views.video_stream, name='video_stream'),
    path('live_stream/', views.live_stream, name='live_stream'),
    path('stream_status/', views.stream_status, name='stream_status'),
    
    # Tests
    path('health/', views.test_endpoint, name='health_check'),
    path('test/', views.test_endpoint, name='test'),
]
