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
from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class DjangoHugoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_hugo"
    verbose_name = _("Django Hugo")

    def ready(self):
        # Ensure that the app is registered before accessing its models
        if not apps.ready:
            return

        # Import the signals and tasks to ensure they are registered
        from . import signals, tasks  # noqa: F401
