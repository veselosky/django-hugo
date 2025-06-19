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
from django.urls import path

from django_hugo.sites import views

urlpatterns = [
    path(
        "create/",
        views.HugoSiteCreateView.as_view(),
        name="hugo_site_create",
    ),
    # path("hugo/<slug:site_slug>/build/", views.hugo_build, name="hugo_build"),
    # path("hugo/<slug:site_slug>/logs/", views.hugo_logs, name="hugo_logs"),
    path(
        "<slug:slug>/delete/",
        views.HugoSiteDeleteView.as_view(),
        name="hugo_site_delete",
    ),
    path(
        "<slug:slug>/edit/",
        views.HugoSiteUpdateView.as_view(),
        name="hugo_site_edit",
    ),
    path(
        "<slug:slug>/",
        views.HugoSiteDetailView.as_view(),
        name="hugo_site_detail",
    ),
    path("", views.HugoSiteListView.as_view(), name="hugo_index"),
]
