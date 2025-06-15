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
from django.db import models
from django.utils.translation import gettext_lazy as _

config = apps.get_app_config("django_hugo")
HUGO_THEMES_ROOT = config.THEMES_ROOT


class HugoTheme(models.Model):
    """
    This model represents a Hugo theme that can be used by one or more Hugo sites.
    Themes are stored in the file system and this model provides metadata about them.
    It is expected that themes may be organized in subdirectories under the
    HUGO_THEMES_ROOT directory, and each theme must contain a theme.toml file
    that defines its metadata.

    NOTE: The model itself makes no guarantees about the existence of the theme
    directory or the theme.toml file. It is the responsibility of the application
    to ensure that the themes are properly installed and available in the file system.

    The `relative_dir` field is the path to the theme directory relative to
    the HUGO_THEMES_ROOT directory. This allows for themes to be organized
    in subdirectories while still being uniquely identifiable.

    The `name` field is the human-readable name of the theme, which should be unique.

    The `description` field is optional and can be used to provide additional
    information about the theme.

    The `active` field indicates whether the theme is currently active and can be
    used by Hugo sites. If a theme is not active, it will not be available for
    selection in the Hugo site configuration.

    The `dir_path` property returns a pathlib.Path representing the theme directory.

    The `toml_path` property returns a pathlib.Path representing the theme.toml file
    containing the theme metadata.
    """

    name = models.CharField(
        _("name"), max_length=255, unique=True, help_text=_("Name of the theme")
    )
    relative_dir = models.CharField(
        _("relative directory"),
        max_length=255,
        unique=True,
        help_text=_("Relative path to the theme directory under HUGO_THEMES_ROOT"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Optional description of the Hugo theme"),
    )
    active = models.BooleanField(
        _("active"),
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
        """
        return pathlib.Path(config.THEMES_ROOT).joinpath(self.relative_dir)

    @property
    def toml_path(self) -> pathlib.Path:
        """
        Returns the file system path to the theme.toml file.
        """
        return self.dir_path / "theme.toml"
