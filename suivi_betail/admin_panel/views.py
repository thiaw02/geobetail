from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Count
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from animaux.models import Alerte, Device

from .mixins import AdminRequiredMixin
from .forms import (
    AlerteForm,
    DeviceForm,
    UserCreateForm,
    UserEditForm,
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
        }
        ctx['recent_users'] = users.order_by('-date_joined')[:5]
        ctx['recent_alertes'] = Alerte.objects.filter(resolue=False).order_by('-date_creation')[:5]
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
