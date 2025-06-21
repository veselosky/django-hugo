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
from django_hugo.themes.views import ThemeBrowserView

app_name = "hugo"
urlpatterns = [
    path(
        "create/",
        views.HugoSiteCreateView.as_view(),
        name="site_create",
    ),
    path(
        "themes/",
        ThemeBrowserView.as_view(),
        name="themes",
    ),
    # path("<slug:slug>/build/", views.build, name="build"),
    # path("<slug:slug>/logs/", views.logs, name="logs"),
    path(
        "<slug:slug>/delete/",
        views.HugoSiteDeleteView.as_view(),
        name="site_delete",
    ),
    path(
        "<slug:slug>/edit/",
        views.HugoSiteUpdateView.as_view(),
        name="site_edit",
    ),
    path(
        "<slug:slug>/",
        views.HugoSiteDetailView.as_view(),
        name="site_detail",
    ),
    path("", views.HugoSiteListView.as_view(), name="index"),
]
