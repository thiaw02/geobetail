from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'animaux'

urlpatterns = [
    # ==================== PAGES HTML PRINCIPALES ====================
    path('', views.accueil, name='accueil'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('animaux/', login_required(views.animaux_list), name='animaux_list'),
    path('zones/', login_required(views.mes_zones), name='mes_zones'),
    path('carte/', login_required(views.map_view), name='carte'),
    path('map/', login_required(views.map_view), name='map'),
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('surveillance/', login_required(views.surveillance), name='surveillance'),
    path('camera/', login_required(views.camera_view), name='camera'),
    path('alertes/', login_required(views.alertes), name='alertes'),
    path('profil/', views.profil, name='profil'),
    path('parametres/', views.parametres, name='parametres'),
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    path('colliers/', views.mes_colliers, name='mes_colliers'),
    path('colliers/ajouter/', views.ajouter_collier, name='ajouter_collier'),
    
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
    path('api/zones/creer/', views.create_zone, name='create_zone'),
    path('api/zones/<int:zone_id>/supprimer/', views.delete_zone, name='delete_zone'),
    path('api/alertes/', views.get_alertes, name='alertes'),
    path('api/devices/', views.get_devices, name='devices'),
    
    # ==================== ALIAS COMPATIBILITÉ ANGLAIS/FRANÇAIS ====================
    path('api/animals/active/', views.get_active_animals, name='animals_active_en'),
    path('api/positions/recent/', views.get_recent_positions, name='positions_recent_en'),
    path('api/animals/list/', views.get_animaux_list, name='animals_list_en'),
    path('api/tbeam/latest/', views.get_recent_positions, name='tbeam_latest_en'),
    
    # Alias supplémentaires
    path('api/animaux/list/', views.get_animaux_list, name='animaux_list_alias'),
    path('api/animaux/', views.get_animaux_list, name='animaux_all'),
    path('api/animaux/tous/', views.get_animaux_list, name='animaux_tous'),
    
    # Alias dashboard
    path('api/stats/', views.get_dashboard_stats, name='stats'),
    path('api/dashboard/', views.get_dashboard_stats, name='dashboard_api'),
    path('api/statistiques/', views.get_dashboard_stats, name='statistiques'),
    
    # Alias T-Beam
    path('api/tbeam/dernieres/', views.get_recent_positions, name='tbeam_latest'),
    path('api/tbeam/data/', views.receive_tbeam_data, name='tbeam_data'),
    path('api/device/data/', views.receive_tbeam_data, name='device_data'),
    
    # Endpoints test/santé
    path('api/test/', views.test_endpoint, name='test_endpoint'),
    path('api/health/', views.test_endpoint, name='health_check'),
    path('api/status/', views.test_endpoint, name='api_status'),
]