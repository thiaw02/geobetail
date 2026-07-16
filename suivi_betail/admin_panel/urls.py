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

    # Colliers
    path('colliers/', views.DeviceListView.as_view(), name='device_list'),
    path('colliers/creer/', views.DeviceCreateView.as_view(), name='device_create'),
    path('colliers/<int:pk>/modifier/', views.DeviceUpdateView.as_view(), name='device_update'),
    path('colliers/<int:pk>/supprimer/', views.DeviceDeleteView.as_view(), name='device_delete'),

    # Alertes
    path('alertes/', views.AlerteListView.as_view(), name='alerte_list'),
    path('alertes/<int:pk>/modifier/', views.AlerteUpdateView.as_view(), name='alerte_update'),
    path('alertes/<int:pk>/supprimer/', views.AlerteDeleteView.as_view(), name='alerte_delete'),
]
