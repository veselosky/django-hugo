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
This module contains actions related to Hugo themes.
"""

from pathlib import Path

from django.apps import apps
from django.db import transaction

from django_hugo.themes.config import load_theme_metadata
from django_hugo.themes.models import HugoTheme

config = apps.get_app_config("django_hugo")
HUGO_THEMES_ROOT = config.THEMES_ROOT

__all__ = ["find_theme_files", "sync_themes"]


def find_theme_files(path: Path = HUGO_THEMES_ROOT) -> list[Path]:
    """
    Return a list of all theme.toml files in child directories of the specified path.
    If a subdirectory contains a theme.toml file, it is considered a Hugo theme. Add
    that path to the list. If a subdirectory does not contain a theme.toml file, recurse
    into that subdirectory to find themes.
    """
    theme_files = []
    for item in path.iterdir():
        if item.is_dir():
            theme_file = item / "theme.toml"
            if theme_file.exists():
                theme_files.append(theme_file)
            else:
                theme_files.extend(find_theme_files(item))
    return theme_files


@transaction.atomic
def sync_themes(path: Path = HUGO_THEMES_ROOT):
    """
    Synchronize the themes in the database with the themes available in the file system.
    This will create new HugoTheme instances for any themes found in the file system
    that are not already in the database.
    """
    available_themes = {
        str(theme_file.resolve()): load_theme_metadata(theme_file)
        for theme_file in find_theme_files(path)
    }
    existing_themes = HugoTheme.objects.values_list("toml_path", flat=True)

    for theme_toml, theme in available_themes.items():
        if theme_toml not in existing_themes:
            HugoTheme.objects.create(
                name=theme.name,
                toml_path=theme_toml,
                description=theme.description,
                active=True,
            )

    # deactivate themes that are no longer available
    for existing_theme in existing_themes:
        if existing_theme not in available_themes:
            HugoTheme.objects.filter(toml_path=existing_theme).update(active=False)
