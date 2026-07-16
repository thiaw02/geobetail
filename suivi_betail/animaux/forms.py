import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Profile


TEL_RE = re.compile(r'^\+?\d[\d\s.\-]{6,}$')


def _identifiant_est_email(valeur):
    return '@' in valeur


def _username_unique(base):
    base = re.sub(r'[^a-zA-Z0-9_.-]', '', base) or 'eleveur'
    base = base[:140]
    username = base
    i = 1
    while User.objects.filter(username__iexact=username).exists():
        username = f"{base}{i}"
        i += 1
    return username


class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion : un seul champ identifiant (e-mail/téléphone)."""

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Email/téléphone ou mot de passe incorrect.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email ou téléphone"
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email ou téléphone',
            'autofocus': True,
            'autocomplete': 'username',
            'inputmode': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'autocomplete': 'current-password',
        })


class InscriptionForm(forms.Form):
    """Inscription publique : crée uniquement des comptes de rôle Éleveur."""

    nom_complet = forms.CharField(
        label="Nom complet",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Prénom et nom',
            'autocomplete': 'name', 'autofocus': True,
        }),
    )
    identifiant = forms.CharField(
        label="Email ou téléphone",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'adresse@email.com ou +221…',
            'autocomplete': 'username',
        }),
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Mot de passe',
            'autocomplete': 'new-password', 'id': 'id_password1',
        }),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Confirmer le mot de passe',
            'autocomplete': 'new-password',
        }),
    )
    cgu = forms.BooleanField(
        required=True,
        error_messages={'required': "Vous devez accepter les CGU et la politique de confidentialité."},
    )

    def clean_identifiant(self):
        valeur = self.cleaned_data['identifiant'].strip()
        if _identifiant_est_email(valeur):
            try:
                validate_email(valeur)
            except ValidationError:
                raise forms.ValidationError("Adresse e-mail invalide.")
            if User.objects.filter(email__iexact=valeur).exists():
                raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        else:
            if not TEL_RE.match(valeur):
                raise forms.ValidationError("Entrez un e-mail ou un numéro de téléphone valide.")
            if Profile.objects.filter(telephone=valeur).exists():
                raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return valeur

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        if p1:
            validate_password(p1)
        return p2

    def save(self):
        identifiant = self.cleaned_data['identifiant'].strip()
        nom = self.cleaned_data['nom_complet'].strip()
        est_email = _identifiant_est_email(identifiant)

        if est_email:
            base = identifiant.split('@')[0]
        else:
            base = 'eleveur' + re.sub(r'\D', '', identifiant)

        user = User(username=_username_unique(base))
        if est_email:
            user.email = identifiant
        parts = nom.split(' ', 1)
        user.first_name = parts[0][:150]
        user.last_name = (parts[1] if len(parts) > 1 else '')[:150]
        user.set_password(self.cleaned_data['password1'])
        user.save()  # crée le profil via signal

        profile = user.profile
        profile.role = Profile.ROLE_ELEVEUR
        if not est_email:
            profile.telephone = identifiant
        profile.save()
        return user


class ProfileForm(forms.Form):
    """Modification du profil (nom, e-mail, téléphone, photo)."""

    nom_complet = forms.CharField(label="Nom complet", max_length=150,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Adresse e-mail", required=False,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(label="Téléphone", max_length=30, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    photo = forms.ImageField(label="Photo de profil", required=False,
                             widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user and not self.is_bound:
            full = f"{user.first_name} {user.last_name}".strip() or user.username
            self.fields['nom_complet'].initial = full
            self.fields['email'].initial = user.email
            self.fields['telephone'].initial = getattr(user.profile, 'telephone', '')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone', '').strip()
        if tel and Profile.objects.filter(telephone=tel).exclude(user=self.user).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return tel

    def save(self):
        user = self.user
        nom = self.cleaned_data['nom_complet'].strip()
        parts = nom.split(' ', 1)
        user.first_name = parts[0][:150]
        user.last_name = (parts[1] if len(parts) > 1 else '')[:150]
        user.email = self.cleaned_data.get('email', '')
        user.save()
        profile = user.profile
        profile.telephone = self.cleaned_data.get('telephone', '')
        if self.cleaned_data.get('photo'):
            profile.photo = self.cleaned_data['photo']
        profile.save()
        return user


class SettingsForm(forms.ModelForm):
    """Préférences : langue et canal de notification."""

    class Meta:
        model = Profile
        fields = ['langue', 'notif_canal']
        widgets = {
            'langue': forms.Select(attrs={'class': 'form-control'}),
            'notif_canal': forms.Select(attrs={'class': 'form-control'}),
        }

    LANGUE_CHOICES = [('fr', 'Français'), ('wo', 'Wolof'), ('ff', 'Pulaar')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['langue'] = forms.ChoiceField(
            label="Langue", choices=self.LANGUE_CHOICES,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
