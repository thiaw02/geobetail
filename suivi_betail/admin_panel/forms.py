from django import forms
from django.contrib.auth.models import User

from animaux.models import Alerte, Animal, Device, JournalAudit, SignalementVol, Zone


class StyledFormMixin:
    """Applique automatiquement les classes du design system aux widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                css = 'form-check-group'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            else:
                css = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (existing + ' ' + css).strip()


class UserCreateForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        required=True,
        min_length=8,
        help_text="Au moins 8 caractères.",
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput,
        required=False,
        min_length=8,
        help_text="Laisser vide pour conserver le mot de passe actuel.",
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        pw = self.cleaned_data.get('password')
        if pw:
            user.set_password(pw)
        if commit:
            user.save()
        return user


class DeviceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'device_id', 'nom', 'type_device', 'statut', 'batterie',
            'proprietaire', 'code_appairage', 'est_appaire', 'date_appairage',
        ]
        widgets = {
            'date_appairage': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AnimalForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'nom', 'type_animal', 'race', 'date_naissance',
            'device', 'statut', 'emoji', 'couleur',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }


class ZoneForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Zone
        fields = [
            'nom', 'description', 'type_zone', 'couleur', 'animaux', 'polygone',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'polygone': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'GeoJSON, ex: {"type":"Polygon","coordinates":[[[0,0],[0,1],[1,1],[1,0],[0,0]]]}',
            }),
            'animaux': forms.CheckboxSelectMultiple(),
        }


class SignalementVolForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SignalementVol
        fields = ['animal', 'proprietaire', 'position', 'statut', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        }


class JournalAuditForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = JournalAudit
        fields = ['utilisateur_cible', 'action', 'auteur', 'date', 'detail']
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AlerteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Alerte
        fields = ['animal', 'type_alerte', 'priorite', 'message', 'resolue']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }
