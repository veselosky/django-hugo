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
Model representing a Hugo site managed by this app.
"""

import pathlib

from django.apps import apps
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from django_hugo.themes.models import HugoTheme
from django_hugo.wrapper import HugoWrapper

__all__ = ["HugoSite"]

config = apps.get_app_config("django_hugo")
HUGO_PATH = config.HUGO_PATH
HUGO_THEMES_ROOT = config.THEMES_ROOT
HUGO_SITES_ROOT = config.SITES_ROOT


class HugoSite(models.Model):
    """
    This model is an inventory of Hugo sites managed by this app. The file system is the
    repository of truth about the site, so the model only stores basic metadata needed to
    locate the site source and display the site in the edit interface.
    """

    # User-editable fields that define the Hugo site.
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Administrative name for the Hugo site (not used in Hugo)"),
    )
    slug = models.SlugField(
        _("slug"),
        help_text=_(
            "Slug for the Hugo site (the name of the directory under HUGO_SITE_ROOT)"
        ),
    )
    base_url = models.URLField(
        _("base URL"),
        blank=True,
        help_text=_("Base URL for the Hugo site (used in metadata and links)"),
    )
    title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("Title of the Hugo site (used in the site header and metadata)"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Optional description of the Hugo site"),
    )
    copyright = models.CharField(
        _("copyright"),
        max_length=255,
        blank=True,
        help_text=_("Optional copyright notice for the Hugo site"),
    )
    pager_size = models.PositiveIntegerField(
        _("items per page"),
        default=10,
        help_text=_("Number of items per page in paginated lists"),
    )
    theme = models.ForeignKey(
        HugoTheme,
        verbose_name=_("theme"),
        on_delete=models.PROTECT,
        related_name="hugo_sites",
        help_text=_("The Hugo theme used by this site"),
    )
    enable_emoji = models.BooleanField(
        _("enable emoji"),
        default=True,
        help_text=_("Enable emoji shortcodes like :smiley: in content"),
    )
    enable_robots = models.BooleanField(
        _("generate robots.txt"),
        default=True,
        help_text=_("Generate robots.txt to control search engine indexing"),
    )

    # Internal fields not editable by users, but used by the app to manage the site.
    # Every site MUST belong to a user for permission purposes.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hugo_sites",
        help_text=_("The user who owns this Hugo site"),
    )

    last_published = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("The last time this site was published"),
    )
    archived = models.BooleanField(
        default=False,
        help_text=_("Indicates if the site is archived and not actively used"),
    )
    has_unpublished_changes = models.BooleanField(
        default=False,
        help_text=_("Indicates if the site has unpublished changes"),
    )

    class Meta:
        verbose_name = _("Hugo Site")
        verbose_name_plural = _("Hugo Sites")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "slug"],
                name="unique_user_slug",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL for this Hugo site.
        This is used in the admin interface to link to the site.
        """
        return (
            f"/hugo/{self.slug}/"  # FIXME: When we have views, this should reverse one
        )

    def save(self, *args, **kwargs):
        """
        When we save a site, also make sure the corresponding hugo site exists on disk.
        """
        super().save(*args, **kwargs)
        # Ensure the  site has been created on disk.
        if not self.path.exists():
            toml = render_to_string(
                "hugo/hugo.toml.txt",
                {
                    "site": self,
                    "HUGO_THEMES_ROOT": HUGO_THEMES_ROOT,
                },
            )
            hugo = HugoWrapper(hugo_path=HUGO_PATH)
            hugo.new_site(
                site_name=self.slug,
                toml=toml,
            )

    @property
    def path(self) -> pathlib.Path:
        """
        Returns the file system path to the Hugo site.
        This is used to locate the site source files.
        """
        return HUGO_SITES_ROOT / self.slug
