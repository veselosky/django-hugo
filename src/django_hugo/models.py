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
This module aggregates the models for the Django Hugo application, providing a single
import point for the main models used in the application. It includes models for Hugo sites
and themes, which are essential components for managing Hugo-based static sites within a
Django project.
"""

from django_hugo.sites.models import HugoSite
from django_hugo.themes.models import HugoTheme

__all__ = [
    "HugoSite",
    "HugoTheme",
]
