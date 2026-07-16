"""Helpers de détection de rôle, utilisés côté serveur uniquement."""


def user_is_superuser(user):
    """Superutilisateur Django (accès /admin/)."""
    return bool(getattr(user, 'is_authenticated', False) and getattr(user, 'is_superuser', False))


def user_is_admin_panel(user):
    """Administrateur de l'application admin_panel, sans être superuser Django."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return False
    if user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == 'ADMIN')


def user_is_admin(user):
    """Administrateur plateforme au sens large : superuser Django OU admin_panel."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == 'ADMIN')


def user_is_veterinaire(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == 'VETERINAIRE')


def user_is_eleveur(user):
    """Éleveur : utilisateur authentifié qui n'est ni admin ni vétérinaire."""
    if not getattr(user, 'is_authenticated', False):
        return False
    return not user_is_admin(user) and not user_is_veterinaire(user)


def role_home_url(user):
    """Route d'accueil post-connexion selon le rôle."""
    from django.urls import reverse
    if user_is_superuser(user):
        return reverse('admin:index')
    if user_is_admin_panel(user):
        return reverse('admin_panel:dashboard')
    return reverse('animaux:dashboard')


def role_context(request):
    """Context processor : expose les helpers de rôle aux templates."""
    user = getattr(request, 'user', None)
    return {
        'user_is_admin': bool(user and user_is_admin(user)),
        'user_is_admin_panel': bool(user and user_is_admin_panel(user)),
        'user_is_eleveur': bool(user and user_is_eleveur(user)),
        'user_is_veterinaire': bool(user and user_is_veterinaire(user)),
        'user_is_superuser': bool(user and user_is_superuser(user)),
    }
