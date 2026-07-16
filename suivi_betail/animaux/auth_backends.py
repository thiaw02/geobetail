"""Backend d'authentification acceptant username, e-mail ou téléphone."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrPhoneOrUsernameBackend(ModelBackend):
    """Permet la connexion via le nom d'utilisateur, l'e-mail ou le téléphone.

    Un seul champ « identifiant » est présenté à l'utilisateur ; la détection
    du format se fait ici, côté serveur.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        identifiant = (username or kwargs.get('identifiant') or '').strip()
        if not identifiant or password is None:
            return None

        lookup = (
            Q(username__iexact=identifiant)
            | Q(email__iexact=identifiant)
            | Q(profile__telephone=identifiant)
        )
        try:
            user = User.objects.filter(lookup).distinct().get()
        except User.DoesNotExist:
            # Contre-mesure timing : on hash quand même un mot de passe.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(lookup).order_by('id').first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
