from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from animaux import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Flux d'authentification et de compte (app « animaux ») — inclut /connexion/, /inscription/, etc.
    path('', include('animaux.urls')),

    # Espace de gestion métier (route canonique /admin_panel/)
    path('admin_panel/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),

    # Connexion unifiée (route explicite pour clarté)
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),

    # Connexion espace administration (accès restreint aux admins)
    path('connexion/admin/', views.connexion_admin, name='connexion_admin'),

    # Déconnexion avec confirmation (GET) puis action (POST)
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Flux « mot de passe oublié » en 3 étapes
    path('mot-de-passe-oublie/', views.MotDePasseOublieView.as_view(), name='password_reset'),
    path('mot-de-passe-oublie/confirmation/', views.MotDePasseOublieDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.MotDePasseResetView.as_view(), name='password_reset_confirm'),
    path('mot-de-passe-oublie/termine/', views.MotDePasseResetDoneView.as_view(), name='password_reset_complete'),

    # Redirections des anciennes routes vers les nouvelles
    path('login/', RedirectView.as_view(pattern_name='connexion', query_string=True)),
    path('logout/', RedirectView.as_view(url='/deconnexion/', query_string=True)),
    path('gestion/', RedirectView.as_view(pattern_name='admin_panel:dashboard')),

    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),

    # API Auth
    path('api/token/', views.obtain_token_pair, name='token_obtain_pair'),
    path('api/token/refresh/', views.refresh_token, name='token_refresh'),

    # API v1
    path('api/v1/', include(('animaux.urls_api', 'animaux_api'))),
    path('api/v1/colliers/', include(('animaux.urls_colliers', 'colliers'))),

    # API Documentation
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
