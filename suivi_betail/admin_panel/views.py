from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db.models import Count
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from animaux.models import Alerte, Animal, Device, JournalAudit, SignalementVol, Zone

from .mixins import AdminRequiredMixin
from .forms import (
    AlerteForm,
    AnimalForm,
    DeviceForm,
    JournalAuditForm,
    SignalementVolForm,
    UserCreateForm,
    UserEditForm,
    ZoneForm,
)


# ============================================================================
# Tableau de bord administrateur
# ============================================================================
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        users = User.objects
        ctx['stats'] = {
            'users_total': users.count(),
            'users_staff': users.filter(is_staff=True).count(),
            'users_active': users.filter(is_active=True).count(),
            'devices_total': Device.objects.count(),
            'devices_paired': Device.objects.filter(est_appaire=True).count(),
            'alertes_actives': Alerte.objects.filter(resolue=False).count(),
            'signalements_vol_actifs': SignalementVol.objects.exclude(statut__in=['RESOLU', 'FAUX']).count(),
        }
        ctx['recent_users'] = users.order_by('-date_joined')[:5]
        ctx['recent_alertes'] = Alerte.objects.filter(resolue=False).order_by('-date_creation')[:5]
        ctx['recent_signalements'] = SignalementVol.objects.exclude(statut__in=['RESOLU', 'FAUX']).order_by('-date_creation')[:5]
        return ctx


# ============================================================================
# Utilisateurs
# ============================================================================
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q)
        return qs


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'admin_panel/user_form.html'
    success_url = reverse_lazy('admin_panel:user_list')


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'admin_panel/user_form.html'
    success_url = reverse_lazy('admin_panel:user_list')


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:user_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Utilisateur'
        return ctx


# ============================================================================
# Colliers (Devices)
# ============================================================================
class DeviceListView(AdminRequiredMixin, ListView):
    model = Device
    template_name = 'admin_panel/device_list.html'
    context_object_name = 'devices'
    paginate_by = 20

    def get_queryset(self):
        qs = Device.objects.select_related('proprietaire').order_by('nom')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nom__icontains=q) | qs.filter(device_id__icontains=q)
        return qs


class DeviceCreateView(AdminRequiredMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'admin_panel/device_form.html'
    success_url = reverse_lazy('admin_panel:device_list')


class DeviceUpdateView(AdminRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'admin_panel/device_form.html'
    success_url = reverse_lazy('admin_panel:device_list')


class DeviceDeleteView(AdminRequiredMixin, DeleteView):
    model = Device
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:device_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Collier'
        return ctx


# ============================================================================
# Alertes
# ============================================================================
class AlerteListView(AdminRequiredMixin, ListView):
    model = Alerte
    template_name = 'admin_panel/alerte_list.html'
    context_object_name = 'alertes'
    paginate_by = 20

    def get_queryset(self):
        return Alerte.objects.select_related('animal').order_by('-date_creation')


class AlerteUpdateView(AdminRequiredMixin, UpdateView):
    model = Alerte
    form_class = AlerteForm
    template_name = 'admin_panel/alerte_form.html'
    success_url = reverse_lazy('admin_panel:alerte_list')


class AlerteDeleteView(AdminRequiredMixin, DeleteView):
    model = Alerte
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:alerte_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Alerte'
        return ctx


# ============================================================================
# Animaux
# ============================================================================
class AnimalListView(AdminRequiredMixin, ListView):
    model = Animal
    template_name = 'admin_panel/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 20

    def get_queryset(self):
        qs = Animal.objects.select_related('device').order_by('nom')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nom__icontains=q)
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        type_animal = self.request.GET.get('type_animal')
        if type_animal:
            qs = qs.filter(type_animal=type_animal)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statut_choices'] = Animal.STATUT_CHOICES
        ctx['type_animal_choices'] = Animal.TYPE_ANIMAL_CHOICES
        return ctx


class AnimalUpdateView(AdminRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'admin_panel/animal_form.html'
    success_url = reverse_lazy('admin_panel:animal_list')


class AnimalDeleteView(AdminRequiredMixin, DeleteView):
    model = Animal
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:animal_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Animal'
        return ctx


# ============================================================================
# Zones
# ============================================================================
class ZoneListView(AdminRequiredMixin, ListView):
    model = Zone
    template_name = 'admin_panel/zone_list.html'
    context_object_name = 'zones'
    paginate_by = 20

    def get_queryset(self):
        return Zone.objects.order_by('nom')


class ZoneUpdateView(AdminRequiredMixin, UpdateView):
    model = Zone
    form_class = ZoneForm
    template_name = 'admin_panel/zone_form.html'
    success_url = reverse_lazy('admin_panel:zone_list')


class ZoneDeleteView(AdminRequiredMixin, DeleteView):
    model = Zone
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:zone_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Zone de pâturage'
        return ctx


class ZoneDetachAnimalsView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/zone_detach_animals.html'

    def get(self, request, *args, **kwargs):
        zone = get_object_or_404(Zone, pk=kwargs['pk'])
        animaux = Animal.objects.filter(zone=zone)
        return render(request, self.template_name, {'zone': zone, 'animaux': animaux})

    def post(self, request, *args, **kwargs):
        zone = get_object_or_404(Zone, pk=kwargs['pk'])
        animal_id = request.POST.get('animal_id')
        if animal_id:
            Animal.objects.filter(pk=animal_id, zone=zone).update(zone=None)
            messages.success(request, "Animal retiré de la zone.")
        else:
            count = Animal.objects.filter(zone=zone).count()
            Animal.objects.filter(zone=zone).update(zone=None)
            messages.success(request, f"{count} animal(retiré(s) de la zone « {zone.nom} ».")
        return redirect('admin_panel:zone_list')


# ============================================================================
# Signalements de vol
# ============================================================================
class SignalementVolListView(AdminRequiredMixin, ListView):
    model = SignalementVol
    template_name = 'admin_panel/signalementvol_list.html'
    context_object_name = 'signalements'
    paginate_by = 20

    def get_queryset(self):
        return SignalementVol.objects.select_related('animal', 'proprietaire').order_by('-date_creation')


class SignalementVolUpdateView(AdminRequiredMixin, UpdateView):
    model = SignalementVol
    form_class = SignalementVolForm
    template_name = 'admin_panel/signalementvol_form.html'
    success_url = reverse_lazy('admin_panel:signalementvol_list')


class SignalementVolDeleteView(AdminRequiredMixin, DeleteView):
    model = SignalementVol
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:signalementvol_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.success_url
        ctx['obj_type'] = 'Signalement de vol'
        return ctx


# ============================================================================
# Journaux d'audit
# ============================================================================
class JournalAuditListView(AdminRequiredMixin, ListView):
    model = JournalAudit
    template_name = 'admin_panel/journalaudit_list.html'
    context_object_name = 'journaux'
    paginate_by = 20

    def get_queryset(self):
        return JournalAudit.objects.select_related('utilisateur_cible', 'auteur').order_by('-date')
