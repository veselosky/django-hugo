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
import logging
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
__all__ = ["DjangoHugoConfig"]


class DjangoHugoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_hugo"
    verbose_name = _("Django Hugo")

    def ready(self):
        logger.debug("DjangoHugoConfig in ready; loading checks, signals, and tasks")
        # Import the checks, signals, and tasks to ensure they are registered
        from . import checks, signals, tasks  # noqa: F401

    @property
    def SITES_ROOT(self) -> Path:
        """
        Returns the root directory for Hugo sites.
        This is configurable via the HUGO_SITES_ROOT setting.
        """
        # Note: Will raise an error if the setting is not defined
        return Path(settings.HUGO_SITES_ROOT)

    @property
    def THEMES_ROOT(self) -> Path:
        """
        Returns the root directory for Hugo themes.
        This is configurable via the HUGO_THEMES_ROOT setting.
        """
        # Note: Will raise an error if the setting is not defined
        return Path(settings.HUGO_THEMES_ROOT)

    @property
    def HUGO_PATH(self) -> Path:
        """
        Returns the path to the Hugo executable.
        This is configurable via the HUGO_PATH setting.
        """
        # Note: Will raise an error if the setting is not defined
        return Path(settings.HUGO_PATH)

    @property
    def HUGO_COMMAND_TIMEOUT(self) -> int:
        """
        Returns the timeout for Hugo commands in seconds.
        This is configurable via the HUGO_COMMAND_TIMEOUT setting.
        """
        return getattr(settings, "HUGO_COMMAND_TIMEOUT", 30)
