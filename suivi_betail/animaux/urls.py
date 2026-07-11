from django.urls import path

from . import views

app_name = 'animaux'

urlpatterns = [
    # ==================== PAGES HTML PRINCIPALES ====================
    path('', views.accueil, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('animaux/', views.animaux_list, name='animaux_list'),
    path('carte/', views.map_view, name='carte'),
    path('map/', views.map_view, name='map'),
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('surveillance/', views.surveillance, name='surveillance'),
    path('camera/', views.camera_view, name='camera'),
    
    # ==================== SURVEILLANCE VISUELLE ====================
    path('surveillance-visuelle/', views.surveillance, name='surveillance'),
    
    # ==================== API STREAMING VIDÉO ====================
    path('api/upload_image/', views.upload_image, name='upload_image'),
    path('api/video_stream/', views.video_stream, name='video_stream'),
    path('api/live_stream/', views.live_stream, name='live_stream'),
    path('api/stream_status/', views.stream_status, name='stream_status'),
    
    # ==================== API T-BEAM ====================
    path('api/tbeam/stream/', views.receive_tbeam_data, name='receive_tbeam_data'),
    path('api/firmware/update/', views.firmware_update, name='firmware_update'),
    
    # ==================== API FRANÇAIS PRINCIPALE ====================
    path('api/animaux/actifs/', views.get_active_animals, name='active_animals'),
    path('api/positions/recentes/', views.get_recent_positions, name='recent_positions'),
    path('api/dashboard/stats/', views.get_dashboard_stats, name='dashboard_stats'),
    path('api/animaux/liste/', views.get_animaux_list, name='animaux_list_api'),
    path('api/zones/', views.get_zones, name='zones'),
    path('api/alertes/', views.get_alertes, name='alertes'),
    path('api/devices/', views.get_devices, name='devices'),
    
    # ==================== ALIAS COMPATIBILITÉ ANGLAIS/FRANÇAIS ====================
    # Pour le frontend et les applications externes
    path('api/animals/active/', views.get_active_animals, name='animals_active_en'),
    path('api/positions/recent/', views.get_recent_positions, name='positions_recent_en'),
    path('api/animals/list/', views.get_animaux_list, name='animals_list_en'),
    path('api/tbeam/latest/', views.get_recent_positions, name='tbeam_latest_en'),
    
    # Alias supplémentaires pour différentes orthographes
    path('api/animaux/list/', views.get_animaux_list, name='animaux_list_alias'),
    path('api/animaux/', views.get_animaux_list, name='animaux_all'),
    path('api/animaux/tous/', views.get_animaux_list, name='animaux_tous'),
    
    # ==================== ALIAS DASHBOARD ET STATISTIQUES ====================
    path('api/stats/', views.get_dashboard_stats, name='stats'),
    path('api/dashboard/', views.get_dashboard_stats, name='dashboard_api'),
    path('api/statistiques/', views.get_dashboard_stats, name='statistiques'),
    
    # ==================== ALIAS T-BEAM ====================
    path('api/tbeam/dernieres/', views.get_recent_positions, name='tbeam_latest'),
    path('api/tbeam/data/', views.receive_tbeam_data, name='tbeam_data'),
    path('api/device/data/', views.receive_tbeam_data, name='device_data'),
    
    # ==================== ENDPOINT DE TEST ET SANTÉ ====================
    path('api/test/', views.test_endpoint, name='test_endpoint'),
    path('api/health/', views.test_endpoint, name='health_check'),
    path('api/status/', views.test_endpoint, name='api_status'),
]