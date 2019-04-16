from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from classes.models import Class
from learning_emporium.decorators import teacher_required
from users.models import User

from .forms import VaultForm, ClassForm, ScheduledClassForm
from .models import Vault, Class, ScheduledClass


#### CREATE VIEWS
class ClassCreateView(LoginRequiredMixin, CreateView):
    def get_success_url(self):
        return reverse('class-detail', kwargs={'pk': self.object.pk}) 
    model = Class
    fields = [
        'class_name',
        'description',
        'expectations',
        ]   

    def form_valid(self, form):
        form.instance.who_created = self.request.user
        form.instance.who_modified = self.request.user
        return super().form_valid(form)


class ScheduledClassCreateView(LoginRequiredMixin, CreateView):
    model = ScheduledClass
    context_object_name = 'class'
    fields = [
        'teacher',
        'start_date',
        'end_date',
        'start_time',
        'active',
        ]

    def get_context_data(self, **kwargs):
        context = super(ScheduledClassCreateView, self).get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_name_queryset = Class.objects.filter(pk=class_id).values('class_name')
        for name in class_name_queryset:
            class_name = name['class_name']
        context['class_name'] = class_name
        return context

    def form_valid(self, form):
        class_id = self.kwargs['class_id']
        form.instance.class_id = Class(class_id)
        form.instance.who_created = self.request.user
        form.instance.who_modified = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('scheduled-class-detail', kwargs={'pk': self.object.pk})    
    

class VaultCreateView(LoginRequiredMixin, CreateView): 
    model = Vault
    context_object_name = 'class'
    fields = [
        'name',
        'number',
        ]
 
    def get_context_data(self, **kwargs):
        context = super(VaultCreateView, self).get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_name_queryset = Class.objects.filter(pk=class_id).values('class_name')
        for name in class_name_queryset:
            class_name = name['class_name']
        context['class_name'] = class_name
        return context

    def form_valid(self, form, *args, **kwargs):
        class_id = self.kwargs['class_id']
        form.instance.class_id = Class(class_id)
        form.instance.who_created = self.request.user
        form.instance.who_modified = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('vault-detail', kwargs={'pk': self.object.pk})

#### LIST VIEWS
class ClassListView(ListView):
    model = Class
    template_name = 'classes/all_classes'
    context_object_name = 'classes'


class ScheduledClassListView(ListView):
    model = ScheduledClass
    template_name = 'classes/all_scheduled_classes'
    context_object_name = 'all_scheduled_classes'

       
class VaultListView(ListView):
    model = Vault
    template_name = 'vaults/all_vaults'
    context_object_name = 'vaults'


#### DETAIL VIEWS
class ClassDetailView(DetailView):
    model = Class
    def get_context_data(self, **kwargs):
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        print(f'this is the pk variable: {pk}')
        vaults = Vault.objects.filter(class_id=pk)
        print(f'this is the vaults variable: {vaults.query}')
        # for name in vault_queryset:
        #     vault_name = name['vault_name']
        context['vaults'] = vaults
        return context


class ScheduledClassDetailView(DetailView):
    model = ScheduledClass
    context_object_name = 'class_id'


class VaultDetailView(DetailView):
    model = Vault
    context_object_name = 'class_id'


#### UPDATE VIEWS
class ClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Class
    fields = [
        'class_name',
        'description',
        'expectations',
        ]

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        update_class = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
        return False


class ScheduledClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def get_success_url(self):
        return reverse('scheduled-class-update', kwargs={'pk': self.object.pk}) 
    
    model = ScheduledClass
    fields = [
        'class_id',
        'teacher',
        'start_date',
        'end_date',
        'start_time',
        'active',
        ]

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        update_scheduled_class = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
        return False


class VaultUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vault
    fields = [
        'name',
        'number',
        'class_id',
        ]

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        update_vault = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
        return False


#### DELETE VIEWS
class ClassDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Class
    success_url = '/classes/all_classes'

    def test_func(self):
        update_scheduled_class = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
        return False


class ScheduledClassDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ScheduledClass
    success_url = '/classes/all_scheduled_classes'

    def test_func(self):
        update_scheduled_class = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
        return False


class VaultDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vault
    success_url = '/classes/all_vaults'

    def test_func(self):
        update_vault = self.get_object()
        user = CuserMiddleware.get_user()
        if user.is_teacher or user.is_admin:
            return True
return False