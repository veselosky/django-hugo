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
from django.apps import apps
from django.core.management.base import BaseCommand

from django_hugo.themes.actions import sync_themes

config = apps.get_app_config("django_hugo")


class Command(BaseCommand):
    """
    What this command does:
    - For each Hugo site in the database, check if the corresponding files exist.
    - If files are missing, log a warning.
    - If files are present, ensure the database is in sync with the Hugo files.
    - If the database is not in sync, update the database with the latest data from the Hugo files.
    - If the database is in sync, log a success message.
    - For each Hugo theme in the database, check if the corresponding files exist.
    - If theme files are missing, log a warning.
    - If theme files are present, ensure the database is in sync with the Hugo theme files.
    - For each directory in the HUGO_THEMES_DIR setting, check if a Theme model exists
    - If a Theme model does not exist, create it with the appropriate metadata.
    """

    help = "Ensures the Django database is in sync with Hugo files."

    def add_arguments(self, parser):
        return super()

    def handle(self, *args, **options):
        """
        Main entry point for the command.
        """
        # Sync Hugo themes
        sync_themes(config.THEMES_ROOT)
