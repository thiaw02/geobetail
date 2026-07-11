from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from animaux import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('animaux.urls', 'animaux'), namespace='animaux')),  # Routes de l'app animaux
    path('inscription/', views.inscription, name='inscription'),
    path('login/', auth_views.LoginView.as_view(template_name='animaux/login.html'), name='login'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
