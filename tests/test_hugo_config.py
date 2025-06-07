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
Test Hugo configuration model.
"""

from __future__ import annotations

import unittest

from django_hugo.sites.config import (
    HugoConfig,
    hugo_config_to_toml,
    toml_to_hugo_config,
)

# A sample of a reasonably complex Hugo configuration file for testing purposes.
paige_config = """
baseurl = "https://example.com"
enablerobotstxt = true
timezone = "America/Los_Angeles"
titlecasestyle = "Go"

[languages.en]
copyright = "© Will Faught"
languagecode = "en-us"
languagedirection = "ltr"
languagename = "English"
title = "Paige"
weight = 10

[languages.en.params.paige.site]
description = "Powerful, pliable pixel perfection"

[markup.goldmark.renderer]
unsafe = true

[markup.highlight]
noclasses = false
style = "github"

[[module.imports]]
path = "github.com/willfaught/paige"

[outputs]
home = ["atom", "html", "paige-search", "rss"]
section = ["atom", "html", "rss"]
taxonomy = ["atom", "html", "rss"]
term = ["atom", "html", "rss"]

[pagination]
pagersize = 50

[[params.paige.feeds.atom.authors]]
email = "example@example.com"
name = "John Doe"
url = "https://example.com"

[params.paige.feeds.rss]
managing_editor = "example@example.com (John Doe)"
web_master = "example@example.com (John Doe)"

[params.paige.pages]
disable_authors = true
disable_date = true
disable_keywords = true
disable_next = true
disable_prev = true
disable_reading_time = true
disable_series = true
disable_toc = true
disable_word_count = true

[paige.pages.base_schema]
isAccessibleForFree = true
isFamilyFriendly = true

[params.paige.site]
disable_breadcrumbs = true
disable_credit = true

[params.paige.subpages]
disable_authors = true
disable_date = true
disable_keywords = true
disable_reading_time = true
disable_series = true
disable_summary = true
disable_word_count = true

[taxonomies]
author = "authors"
category = "categories"
series = "series"
tag = "tags"
"""


class TestHugoConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config: HugoConfig = toml_to_hugo_config(paige_config)

    def test_baseurl(self) -> None:
        # Check that baseurl was parsed correctly (using proper field alias in HugoConfig)
        # Note that it parses as an HttpUrl, so we must convert to str.
        self.assertEqual(str(self.config.baseURL), "https://example.com/")

    def test_languages(self) -> None:
        languages = self.config.languages or {}
        self.assertIn("en", languages)
        lang_en = languages["en"]
        self.assertEqual(lang_en.get("languagecode"), "en-us")
        self.assertEqual(lang_en.get("languagename"), "English")
        # Validate nested paige.site parameters
        desc = (
            lang_en.get("params", {})
            .get("paige", {})
            .get("site", {})
            .get("description")
        )
        self.assertEqual(desc, "Powerful, pliable pixel perfection")

    def test_params_paige_pages(self) -> None:
        paige = self.config.params.get("paige")
        self.assertIsInstance(paige, dict)
        pages = paige.get("pages", {}) if isinstance(paige, dict) else {}
        # If the parsed structure is a Pydantic model, access attributes accordingly.
        # Here we assume the conversion preserves booleans as defined.
        self.assertTrue(pages.get("disable_authors"))
        self.assertTrue(pages.get("disable_date"))
        self.assertTrue(pages.get("disable_keywords"))
        self.assertTrue(pages.get("disable_next"))
        self.assertTrue(pages.get("disable_prev"))
        self.assertTrue(pages.get("disable_reading_time"))
        self.assertTrue(pages.get("disable_series"))
        self.assertTrue(pages.get("disable_toc"))
        self.assertTrue(pages.get("disable_word_count"))

    def test_taxonomies(self) -> None:
        taxonomies = self.config.taxonomies or {}
        self.assertEqual(taxonomies.get("author"), "authors")
        self.assertEqual(taxonomies.get("category"), "categories")
        self.assertEqual(taxonomies.get("series"), "series")
        self.assertEqual(taxonomies.get("tag"), "tags")


class TestHugoConfigConversion(unittest.TestCase):
    def test_round_trip_integrity(self) -> None:
        # Convert from TOML to HugoConfig instance
        config_initial: HugoConfig = toml_to_hugo_config(paige_config)
        # Convert HugoConfig instance back to TOML string
        toml_output: str = hugo_config_to_toml(config_initial)
        # Convert back to HugoConfig from the TOML output
        config_round_trip: HugoConfig = toml_to_hugo_config(toml_output)
        # Compare a few key fields to ensure round-trip integrity
        self.assertEqual(config_initial.baseURL, config_round_trip.baseURL)
        self.assertEqual(config_initial.timeZone, config_round_trip.timeZone)
        # Additional comparisons can be added as necessary

    def test_invalid_toml_raises_error(self) -> None:
        invalid_toml: str = "this is not valid TOML"
        with self.assertRaises(Exception):
            toml_to_hugo_config(invalid_toml)

    def test_hugo_config_to_toml_output(self) -> None:
        config: HugoConfig = toml_to_hugo_config(paige_config)
        toml_string: str = hugo_config_to_toml(config)
        # Ensure that the output TOML string is not empty and contains key expected substrings.
        self.assertTrue(toml_string)
        self.assertIn("baseURL", toml_string)
        self.assertIn("languages.en", toml_string)


if __name__ == "__main__":
    unittest.main()
