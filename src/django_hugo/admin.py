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
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django_hugo.models import HugoSite, HugoTheme


@admin.register(HugoSite)
class HugoSiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "user",
        "theme",
        "date_published",
        "date_modified",
        "is_archived",
        "has_unpublished_changes",
    )
    list_filter = ("is_archived", "theme", "user")
    search_fields = ("name", "slug", "title", "description")
    readonly_fields = ("date_published", "has_unpublished_changes", "is_archived")
    # TODO: actions = ["publish_site", "archive_site"]
    fieldsets = (
        (
            _("Site Information"),
            {
                "fields": (
                    "name",
                    "slug",
                    "base_url",
                    "title",
                    "description",
                    "copyright",
                    "pager_size",
                    "theme",
                    "enable_emoji",
                    "enable_robots",
                )
            },
        ),
        (
            _("Ownership & Status"),
            {
                "fields": (
                    "user",
                    "date_published",
                    "is_archived",
                    "has_unpublished_changes",
                )
            },
        ),
    )


@admin.register(HugoTheme)
class HugoThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "description")
    list_filter = ("active",)
    search_fields = ("name", "description")
    readonly_fields = ()
    fieldsets = (
        (
            _("Theme Information"),
            {
                "fields": (
                    "name",
                    "toml_path",
                    "description",
                    "active",
                )
            },
        ),
    )
