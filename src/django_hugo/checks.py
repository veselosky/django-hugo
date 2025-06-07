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
from pathlib import Path

from django.core.checks import Error, register


@register()
def check_hugo_settings(app_configs, **kwargs):
    errors = []
    from django.conf import settings

    sites_root = getattr(settings, "HUGO_SITES_ROOT", None)
    themes_root = getattr(settings, "HUGO_THEMES_ROOT", None)
    if sites_root is None:
        errors.append(
            Error(
                "HUGO_SITES_ROOT setting is not defined.",
                hint="Please define HUGO_SITES_ROOT in your settings.py.",
                id="django_hugo.E001",
            )
        )
    else:
        sites_root = Path(sites_root)
        if not sites_root.is_absolute():
            errors.append(
                Error(
                    "HUGO_SITES_ROOT must be an absolute path.",
                    hint="Please provide an absolute path for HUGO_SITES_ROOT.",
                    id="django_hugo.E002",
                )
            )
        if not sites_root.exists():
            errors.append(
                Error(
                    "HUGO_SITES_ROOT does not exist.",
                    hint="Please ensure the directory exists.",
                    id="django_hugo.E003",
                )
            )

    if themes_root is None:
        errors.append(
            Error(
                "HUGO_THEMES_ROOT setting is not defined.",
                hint="Please define HUGO_THEMES_ROOT in your settings.py.",
                id="django_hugo.E011",
            )
        )
    else:
        themes_root = Path(themes_root)
        if not themes_root.is_absolute():
            errors.append(
                Error(
                    "HUGO_THEMES_ROOT must be an absolute path.",
                    hint="Please provide an absolute path for HUGO_THEMES_ROOT.",
                    id="django_hugo.E012",
                )
            )
        if not themes_root.exists():
            errors.append(
                Error(
                    "HUGO_THEMES_ROOT does not exist.",
                    hint="Please ensure the directory exists.",
                    id="django_hugo.E013",
                )
            )

    return errors
