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

from django.core.checks import Error, Tags, Warning, register

from django_hugo.wrapper import HugoWrapper


@register(Tags.files)
def check_hugo_settings(app_configs, **kwargs):
    if app_configs is not None and "django_hugo" not in {
        app.name for app in app_configs
    }:
        # This check is only relevant if django_hugo is installed
        return []

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
        if not sites_root.exists():
            errors.append(
                Error(
                    f"HUGO_SITES_ROOT='{sites_root}' does not exist.",
                    hint="Please ensure the directory exists.",
                    id="django_hugo.E002",
                )
            )
        else:
            # Test that we can write to HUGO_SITES_ROOT
            test_file = sites_root / ".hugo_test_write.txt"
            try:
                with open(test_file, "w") as f:
                    f.write("Hugo test write.")
            except Exception:
                errors.append(
                    Error(
                        f"Cannot write to HUGO_SITES_ROOT='{sites_root}'",
                        hint="Please check the permissions of the directory.",
                        id="django_hugo.E003",
                    )
                )
            else:
                # Clean up the test file
                test_file.unlink(missing_ok=True)

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
        if not themes_root.exists():
            errors.append(
                Error(
                    f"HUGO_THEMES_ROOT='{themes_root}' does not exist.",
                    hint="Please ensure the directory exists.",
                    id="django_hugo.E012",
                )
            )
        else:
            # Check that at least one theme exists
            from django_hugo.themes.actions import find_theme_files

            theme_files = find_theme_files(themes_root)
            if not theme_files:
                errors.append(
                    Error(
                        f"No themes found in HUGO_THEMES_ROOT='{themes_root}'",
                        hint="You need to install at least one theme for django_hugo to use.",
                        id="django_hugo.E013",
                    )
                )

    # Check Hugo version
    hugo_path = getattr(settings, "HUGO_PATH", None)
    if hugo_path is None:
        errors.append(
            Error(
                "HUGO_PATH setting is not defined.",
                hint="Please define HUGO_PATH in your settings.py.",
                id="django_hugo.E004",
            )
        )
    else:
        hugo_path = Path(hugo_path)
        if not hugo_path.exists():
            errors.append(
                Error(
                    f"HUGO_PATH='{hugo_path}' does not exist.",
                    hint="Please ensure the Hugo executable path is correct.",
                    id="django_hugo.E005",
                )
            )
        else:
            try:
                hugo = HugoWrapper(hugo_path)
                warning = hugo.check_version()
                if warning:
                    errors.append(
                        Warning(
                            warning,
                            hint="Consider upgrading Hugo to the latest version.",
                            id="django_hugo.E006",
                        )
                    )
            except RuntimeError:
                errors.append(
                    Error(
                        "Unable to determine Hugo version.",
                        hint=f"Ensure the `HUGO_PATH={hugo_path}` is correct and this user has permission to execute Hugo.",
                        id="django_hugo.E008",
                    )
                )
    return errors
