from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Tableau de bord
    path('', views.AdminDashboardView.as_view(), name='dashboard'),

    # Utilisateurs
    path('utilisateurs/', views.UserListView.as_view(), name='user_list'),
    path('utilisateurs/creer/', views.UserCreateView.as_view(), name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.UserUpdateView.as_view(), name='user_update'),
    path('utilisateurs/<int:pk>/supprimer/', views.UserDeleteView.as_view(), name='user_delete'),

    # Animaux
    path('animaux/', views.AnimalListView.as_view(), name='animal_list'),
    path('animaux/<int:pk>/modifier/', views.AnimalUpdateView.as_view(), name='animal_update'),
    path('animaux/<int:pk>/supprimer/', views.AnimalDeleteView.as_view(), name='animal_delete'),

    # Colliers
    path('colliers/', views.DeviceListView.as_view(), name='device_list'),
    path('colliers/creer/', views.DeviceCreateView.as_view(), name='device_create'),
    path('colliers/<int:pk>/modifier/', views.DeviceUpdateView.as_view(), name='device_update'),
    path('colliers/<int:pk>/supprimer/', views.DeviceDeleteView.as_view(), name='device_delete'),

    # Zones
    path('zones/', views.ZoneListView.as_view(), name='zone_list'),
    path('zones/<int:pk>/modifier/', views.ZoneUpdateView.as_view(), name='zone_update'),
    path('zones/<int:pk>/supprimer/', views.ZoneDeleteView.as_view(), name='zone_delete'),
    path('zones/<int:pk>/retirer-animaux/', views.ZoneDetachAnimalsView.as_view(), name='zone_detach_animals'),

    # Alertes
    path('alertes/', views.AlerteListView.as_view(), name='alerte_list'),
    path('alertes/<int:pk>/modifier/', views.AlerteUpdateView.as_view(), name='alerte_update'),
    path('alertes/<int:pk>/supprimer/', views.AlerteDeleteView.as_view(), name='alerte_delete'),

    # Signalements de vol
    path('signalements-vol/', views.SignalementVolListView.as_view(), name='signalementvol_list'),
    path('signalements-vol/<int:pk>/modifier/', views.SignalementVolUpdateView.as_view(), name='signalementvol_update'),
    path('signalements-vol/<int:pk>/supprimer/', views.SignalementVolDeleteView.as_view(), name='signalementvol_delete'),

    # Journaux d'audit
    path('journaux/', views.JournalAuditListView.as_view(), name='journalaudit_list'),
]
