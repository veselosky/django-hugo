# AGPL Notice: This file is part of django-hugo.
# Copyright (C) 2025 Vincent Veselosky
#
# This package is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this package.  If not, see <https://www.gnu.org/licenses/>.
"""
This module implements the List, Detail, Create, Update, and Delete views for managing
Hugo sites within the app.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from django_hugo.sites.forms import HugoSiteForm
from django_hugo.sites.models import HugoSite

__all__ = [
    "HugoSiteListView",
    "HugoSiteDetailView",
    "HugoSiteCreateView",
    "HugoSiteUpdateView",
    "HugoSiteDeleteView",
]


class HugoSiteListView(LoginRequiredMixin, ListView):
    model = HugoSite
    template_name = "hugo/sites/site_list.html"
    context_object_name = "sites"
    paginate_by = 10

    def get_queryset(self):
        # TODO: Implement filtering by user
        return self.model.objects.filter(user=self.request.user)


class HugoSiteDetailView(LoginRequiredMixin, DetailView):
    model = HugoSite
    template_name = "hugo/sites/site_detail.html"
    context_object_name = "site"

    def get_queryset(self):
        # Ensure the user can only see their own sites
        return self.model.objects.filter(user=self.request.user)


class HugoSiteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HugoSite
    form_class = HugoSiteForm
    template_name = "hugo/sites/site_form.html"
    success_message = _("Hugo site created successfully.")

    def form_valid(self, form):
        form.instance.user = (
            self.request.user
        )  # Set the user to the current logged-in user
        return super().form_valid(form)


class HugoSiteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HugoSite
    form_class = HugoSiteForm
    template_name = "hugo/sites/site_form.html"
    success_url = reverse_lazy("hugo:site_list")
    success_message = _("Hugo site updated successfully.")

    def get_queryset(self):
        # Ensure the user can only update their own sites
        return self.model.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = (
            self.request.user
        )  # Ensure the user is set to the current logged-in user
        return super().form_valid(form)


# TODO: Sites cannot be deleted unless they have been archived first.
class HugoSiteDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = HugoSite
    template_name = "hugo/sites/site_confirm_delete.html"
    success_url = reverse_lazy("hugo:site_list")
    success_message = _("Hugo site deleted successfully.")

    def get_queryset(self):
        # Ensure the user can only delete their own sites
        return self.model.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        self.messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)
