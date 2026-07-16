import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

logger = logging.getLogger('geobetail.security')


class AdminRequiredMixin(LoginRequiredMixin):
    """Accès réservé aux administrateurs de la plateforme.

    Un administrateur est reconnu par is_staff / is_superuser OU par un
    profil de rôle ADMIN. La vérification a lieu à chaque requête (pas
    seulement après la connexion), côté serveur.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        is_admin = (
            request.user.is_staff
            or request.user.is_superuser
            or getattr(getattr(request.user, 'profile', None), 'role', None) == 'ADMIN'
        )
        if not is_admin:
            logger.warning(
                "Accès refusé à /admin_panel/ pour %s (rôle=%s)",
                request.user.username or "anonyme",
                getattr(getattr(request.user, 'profile', None), 'role', None),
            )
            raise PermissionDenied("Accès réservé aux administrateurs de la plateforme.")
        logger.info("Accès /admin_panel/ par %s | %s", request.user.username, request.path)
        return super().dispatch(request, *args, **kwargs)
