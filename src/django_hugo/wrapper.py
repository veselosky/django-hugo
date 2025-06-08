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
This module provides the HugoWrapper class, which is a thin wrapper around the Hugo CLI.
It provides methods to run Hugo commands and manage Hugo sites.
"""

import logging
import re
import subprocess
from pathlib import Path

from django.apps import apps

from django_hugo.sites.models import HugoSite

logger = logging.getLogger(__name__)
config = apps.get_app_config("django_hugo")
version_regex = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")


class HugoWrapper:
    """
    A thin wrapper around the Hugo CLI to manage Hugo sites.
    """

    def __init__(self, hugo_path, site: HugoSite | None = None):
        self.site = site
        # Do not resolve() -- When using snaps, it's a symlink to the snap executable.
        # If called with wrong name, FAIL.
        self.hugo_path = Path(hugo_path)
        if not self.hugo_path.exists():
            raise FileNotFoundError(f"Hugo executable not found at: {self.hugo_path}")
        self.site_path = None
        if site:
            self.site_path = Path(config.SITES_ROOT) / site.slug
            if not self.site_path.exists():
                raise FileNotFoundError(
                    f"Hugo site path does not exist: {self.site_path}"
                )

    def run_command(self, *args) -> str | None:
        """
        Run a Hugo command with the specified arguments.

        Returns:
            str|None: The output of the command if successful, None if it fails.
        """
        command = [str(self.hugo_path)] + list(args)
        if self.site:
            command.append("-s")
            command.append(str(self.site_path))
        logger.info("Running Hugo command: `%s`", " ".join(command))
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=config.HUGO_COMMAND_TIMEOUT,  # Timeout in seconds
            )
        except subprocess.TimeoutExpired as e:
            logger.error("Hugo command timed out after: %s", e.timeout)
            logger.error("Command: `%s`", e.cmd)
            if e.output:
                logger.error("Output: %s", e.output)
            if e.stderr:
                logger.error("Stderr: %s", e.stderr)
            return None
        except subprocess.CalledProcessError as e:
            logger.error("Hugo command failed with return code %d", e.returncode)
            logger.error("Command: `%s`", e.cmd)
            if e.output:
                logger.error("Output: %s", e.output)
            if e.stderr:
                logger.error("Stderr: %s", e.stderr)
            return None
        except Exception as e:
            logger.error("Error running Hugo command: %s", e)
            return None

        logger.info("Hugo command completed successfully")
        if result.stdout:
            logger.info("Output: %s", result.stdout.strip())
        if result.stderr:
            logger.error("Stderr: %s", result.stderr.strip())

        return result.stdout.strip() if result.stdout else None

    def version(self) -> str | None:
        """
        Get the version of Hugo installed.

        Returns:
            str: The Hugo version.
        """
        output = self.run_command("version")
        if output:
            # The version command typically returns something like
            # "hugo v0.147.8-10da2bd765d227761641f94d713d094e88b920ae+extended linux/amd64"
            version_match = version_regex.search(output)
            if version_match:
                version_str = version_match.group("version")
                version = version_str.split(".")
                if "extended" in output:
                    version.append("extended")
                if "deploy" in output:
                    version.append("deploy")
                return ".".join(version)
            else:
                logger.error("Failed to parse Hugo version from output: %s", output)
                return None
        else:
            logger.error("Failed to get Hugo version")
            return None
