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
This implements the Django model for Hugo themes, which are reusable design templates
for Hugo sites. Each theme can be used by multiple sites, and this model provides
metadata about the theme such as its name, file system path, and description.
"""

import pathlib

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

config = apps.get_app_config("django_hugo")
HUGO_THEMES_ROOT = str(config.THEMES_ROOT.resolve())  # Ensure we have an absolute path


class HugoTheme(models.Model):
    """
    This model represents a Hugo theme that can be used by one or more Hugo sites.
    Themes are stored in the file system and this model provides metadata about them.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text=_("Name of the theme")
    )
    toml_path = models.FilePathField(
        path=HUGO_THEMES_ROOT,
        max_length=255,
        recursive=True,
        match=r"^theme\.toml$",
        help_text=_("Path to the theme.toml file within the theme directory"),
    )
    description = models.TextField(
        blank=True, help_text=_("Optional description of the Hugo theme")
    )
    active = models.BooleanField(
        default=True,
        help_text=_("If active, this theme can be used by Hugo sites"),
    )

    class Meta:
        verbose_name = _("Hugo Theme")
        verbose_name_plural = _("Hugo Themes")

    def __str__(self):
        return self.name

    @property
    def dir_path(self) -> pathlib.Path:
        """
        Returns the file system path to the theme directory.
        This is constructed based on the theme's slug and the configured theme root.
        """
        return pathlib.Path(self.toml_path).parent
