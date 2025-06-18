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

logger = logging.getLogger(__name__)
version_regex = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
django_hugo_config = apps.get_app_config("django_hugo")
HUGO_COMMAND_TIMEOUT = django_hugo_config.HUGO_COMMAND_TIMEOUT
HUGO_SITES_ROOT = django_hugo_config.SITES_ROOT


class HugoWrapper:
    """
    A thin wrapper around the Hugo CLI to manage Hugo sites.
    """

    RECOMMENDED_HUGO_VERSION = "0.146.1"  # recommended min version of hugo
    VERSION_WARNING = (
        "The installed Hugo version (%s) is lower than the recommended version (%s). "
        "Some themes may not be compatible. Please consider upgrading Hugo to the "
        "latest version."
    )
    EXTENDED_WARNING = (
        "The installed Hugo version is not the extended version. Some themes may "
        "not be compatible. Please consider installing the extended version of Hugo."
    )

    def __init__(self, hugo_path: str | Path, site: str | Path | None = None):
        self.site_path = None
        if site:
            self.site_path = Path(site)
            if not self.site_path.exists():
                raise FileNotFoundError(
                    f"Hugo site path does not exist: {self.site_path}"
                )

        # Do not resolve() -- When using snaps, it's a symlink to the snap executable.
        # If called with wrong name, FAIL.
        self.hugo_path = Path(hugo_path)
        if not self.hugo_path.exists():
            raise FileNotFoundError(f"Hugo executable not found at: {self.hugo_path}")

    def run_command(self, *args) -> str | None:
        """
        Run a Hugo command with the specified arguments.

        Returns:
            str|None: The output of the command if successful, None if it fails.
        """
        command = [str(self.hugo_path)] + list(args)
        if self.site_path:
            command.append("-s")
            command.append(str(self.site_path))
        logger.info("Running Hugo command: `%s`", " ".join(command))
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=HUGO_COMMAND_TIMEOUT,  # Timeout in seconds
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
            logger.debug("Output: %s", result.stdout.strip())
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

    def check_version(self) -> str:
        """
        Check if the installed Hugo version meets the recommended version.

        Returns:
            str: Empty string if all is well, otherwise a warning message.
        """
        version = self.version()
        if not version:
            raise RuntimeError("Hugo version could not be determined.")

        # Lexical comparison should suffice
        if version < self.RECOMMENDED_HUGO_VERSION:
            logger.warning(
                self.VERSION_WARNING,
                version,
                self.RECOMMENDED_HUGO_VERSION,
            )
            return self.VERSION_WARNING % (version, self.RECOMMENDED_HUGO_VERSION)
        if "extended" not in version:
            logger.warning(self.EXTENDED_WARNING)
            return self.EXTENDED_WARNING

        return ""

    def new_site(self, site_name: str, toml: str | None = None) -> bool:
        """
        Create a new Hugo site.

        Args:
            site_name (str): The name of the new site.

        Returns:
            bool: True if the site was created successfully, False otherwise.
        """
        path = Path(HUGO_SITES_ROOT) / site_name
        if path.exists():
            logger.error("Site path already exists: %s", path)
            return False

        output = self.run_command("new", "site", str(path))
        if output and "Congratulations!" in output:
            logger.info("New Hugo site created at: %s", path)
            if toml:
                # If a toml string is provided, copy it into hugo.toml
                config_path = path / "hugo.toml"
                config_path.write_text(toml)
                logger.info("Config file copied to new site: %s", config_path)
            return True
        else:
            logger.error("Failed to create new Hugo site.")
            return False

    def config(self) -> str | None:
        """
        Get the configuration of the Hugo site.

        Returns:
            str: The configuration of the site.
        """
        # Without a site, hugo will just print its defaults, which is not useful.
        if not self.site_path:
            logger.error("No site specified for getting configuration.")
            return None

        output = self.run_command("config")
        if output:
            return output.strip()
        else:
            logger.error(
                "Failed to get Hugo site configuration for site: %s", self.site_path
            )
            return None

    def build(
        self,
        destination: str | Path | None = None,
        source: str | Path | None = None,
        draft: bool = False,
        environment: str | None = None,
        minify: bool = True,
        verbose: bool = False,
    ) -> bool:
        """
        Build the Hugo site.

        Args:
            destination (str|Path, optional): The destination directory for the build.
                If None, uses the default 'public' directory.
            source (str|Path, optional): The source directory for the build.
                If None, uses the site path.
            draft (bool, optional): If true, include draft and future content.
                Defaults to False.
            environment (str, optional): The environment to use for the build.
                Defaults to None.
            minify (bool, optional): If true, minify the output. Defaults to True.
            verbose (bool, optional): If true, outputs template metrics and hints.
                Defaults to False.

        Returns:
            bool: True if the build was successful, False otherwise.
        """
        command = ["build"]
        if destination:
            command.extend(["-d", str(destination)])

        if source:
            command.extend(["-s", str(source)])
        elif not self.site_path:
            logger.error("No site path specified for building Hugo site.")
            raise ValueError("No site path specified for building Hugo site.")

        if draft:
            command.append("--buildDrafts")
            command.append("--buildFuture")
        if environment:
            command.extend(["--environment", environment])
        if minify:
            command.append("--minify")
        if verbose:
            command.append("--templateMetrics")
            command.append("--templateMetricsHints")

        output = self.run_command(*command)
        if output:
            logger.info("Hugo site (%s) built successfully.", source or self.site_path)
            return True
        else:
            logger.error(
                "Failed to build Hugo site (%s): %s", source or self.site_path, output
            )
            return False
