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
This module is designed to be used with Pydantic v2.

It provides a structured way to define and validate Hugo site configurations,
including site parameters, output formats, taxonomies, menus, and more.
It can be used to load and validate Hugo configuration files, ensuring that
the configuration adheres to the expected structure and types.

Currently supports the most commonly used configurations. Internationalization
and advanced features are not yet implemented, although configs including them should
still validate correctly.

In some happy future where we support importing any random Hugo site, this will have
to be extended to include all possible Hugo configuration options. For now, we only
explicitly define the options we need for django-hugo to function properly.
"""

from __future__ import annotations

from typing import Any

import tomli
import tomli_w
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, HttpUrl

__all__ = [
    "HugoConfig",
    "MenuLink",
    "OutputFormats",
    "MediaType",
    "MarkupGoldmark",
    "MarkupHighlight",
    "MarkupTableOfContents",
    "Markup",
    "Pagination",
    "HTTPCache",
    "BuildConfig",
    "toml_to_hugo_config",
    "hugo_config_to_toml",
]


#######################################################################################
# Pydantic models for Hugo configuration
#######################################################################################


class HTTPCache(BaseModel):
    # Example fields, adjust as needed
    dir: str | None = None
    inMemory: bool | None = Field(
        default=None, validation_alias=AliasChoices("inMemory", "inmemory")
    )
    maxSize: int | None = Field(
        default=None, validation_alias=AliasChoices("maxSize", "maxsize")
    )


class BuildConfig(BaseModel):
    writeStats: bool | None = Field(
        default=None, validation_alias=AliasChoices("writeStats", "writestats")
    )
    useResources: bool | None = Field(
        default=None, validation_alias=AliasChoices("useResources", "useresources")
    )
    writeToDisk: bool | None = Field(
        default=None, validation_alias=AliasChoices("writeToDisk", "writetodisk")
    )


class MenuLink(BaseModel):
    name: str
    url: str
    weight: int | None = None
    identifier: str | None = None
    parent: str | None = None


class OutputFormats(BaseModel):
    # Custom output format definitions
    mediaType: str | None = Field(
        default=None, validation_alias=AliasChoices("mediaType", "mediatype")
    )
    baseName: str | None = Field(
        default=None, validation_alias=AliasChoices("baseName", "basename")
    )
    isPlainText: bool | None = Field(
        default=None, validation_alias=AliasChoices("isPlainText", "isplaintext")
    )
    noUgly: bool | None = Field(
        default=None, validation_alias=AliasChoices("noUgly", "nougly")
    )
    permalinkable: bool | None = None
    isHTML: bool | None = Field(
        default=None, validation_alias=AliasChoices("isHTML", "ishtml")
    )
    isRSS: bool | None = Field(
        default=None, validation_alias=AliasChoices("isRSS", "isrss")
    )
    isJSON: bool | None = Field(
        default=None, validation_alias=AliasChoices("isJSON", "isjson")
    )
    isAMP: bool | None = Field(
        default=None, validation_alias=AliasChoices("isAMP", "isamp")
    )
    rel: str | None = None
    suffix: str | None = None
    protocol: str | None = None


class MediaType(BaseModel):
    suffixes: list[str] | None = None
    delimiter: str | None = None
    mediaType: str | None = Field(
        default=None, validation_alias=AliasChoices("mediaType", "mediatype")
    )
    priority: int | None = None
    charset: str | None = None
    # Additional arbitrary keys
    others: dict[str, Any] | None = None


class MarkupGoldmark(BaseModel):
    renderer: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None
    parser: dict[str, Any] | None = None


class MarkupHighlight(BaseModel):
    noClasses: bool | None = Field(
        default=None, validation_alias=AliasChoices("noClasses", "noclasses")
    )
    guessSyntax: bool | None = Field(
        default=None, validation_alias=AliasChoices("guessSyntax", "guesssyntax")
    )
    hl_Lines: str | None = Field(
        default=None, validation_alias=AliasChoices("hl_Lines", "hl_lines")
    )
    lineNoStart: int | None = Field(
        default=None, validation_alias=AliasChoices("lineNoStart", "linenostart")
    )
    lineNosInTable: bool | None = Field(
        default=None, validation_alias=AliasChoices("lineNosInTable", "linenostable")
    )
    lineNumbers: bool | None = Field(
        default=None, validation_alias=AliasChoices("lineNumbers", "linenumbers")
    )
    style: str | None = None
    tabWidth: int | None = Field(
        default=None, validation_alias=AliasChoices("tabWidth", "tabwidth")
    )


class MarkupTableOfContents(BaseModel):
    endLevel: int | None = Field(
        default=None, validation_alias=AliasChoices("endLevel", "endlevel")
    )
    ordered: bool | None = None
    startLevel: int | None = Field(
        default=None, validation_alias=AliasChoices("startLevel", "startlevel")
    )


class Markup(BaseModel):
    goldmark: MarkupGoldmark | None = None
    highlight: MarkupHighlight | None = None
    tableOfContents: MarkupTableOfContents | None = Field(
        default=None,
        validation_alias=AliasChoices("tableOfContents", "tableofcontents"),
    )


class Pagination(BaseModel):
    pagerSize: int | None = Field(
        default=None, validation_alias=AliasChoices("pagerSize", "pagersize")
    )
    path: str | None = None
    disableAliases: bool | None = Field(
        default=None, validation_alias=AliasChoices("disableAliases", "disablealiases")
    )


class HugoConfig(BaseModel):
    baseURL: HttpUrl = Field(validation_alias=AliasChoices("baseURL", "baseurl"))
    # https://gohugo.io/configuration/build/
    # Probably not needed for django-hugo
    build: BuildConfig | None = None
    buildDrafts: bool | None = Field(
        default=None, validation_alias=AliasChoices("buildDrafts", "builddrafts")
    )
    buildExpired: bool | None = Field(
        default=None, validation_alias=AliasChoices("buildExpired", "buildexpired")
    )
    buildFuture: bool | None = Field(
        default=None, validation_alias=AliasChoices("buildFuture", "buildfuture")
    )
    # https://gohugo.io/configuration/caches/
    # Controls where/how Hugo stores cache data
    caches: dict[str, Any] | None = None
    canonifyURLs: bool | None = Field(
        default=None, validation_alias=AliasChoices("canonifyURLs", "canonifyurls")
    )
    capitalizelistTitles: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("capitalizelistTitles", "capitalizelisttitles"),
    )
    cascade: dict[str, Any] | None = None
    # https://gohugo.io/configuration/content-types/
    # New in v144, ignore for now
    contentTypes: dict[str, Any] | None = Field(
        default=None, validation_alias=AliasChoices("contentTypes", "contenttypes")
    )
    copyright: str | None = None
    defaultContentLanguage: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "defaultContentLanguage", "defaultcontentlanguage"
        ),
    )
    defaultContentLanguageInSubdir: bool | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "defaultContentLanguageInSubdir", "defaultcontentlanguageinsubdir"
        ),
    )
    # https://gohugo.io/configuration/deployment/
    # Used for hugo deploy, not used by django-hugo (yet)
    deployment: dict[str, Any] | None = None
    disableFastRender: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("disableFastRender", "disablefastrender"),
    )
    disableKinds: list[str] | None = Field(
        default=None, validation_alias=AliasChoices("disableKinds", "disablekinds")
    )
    disableLiveReload: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("disableLiveReload", "disablelivereload"),
    )
    enableEmoji: bool | None = Field(
        default=None, validation_alias=AliasChoices("enableEmoji", "enableemoji")
    )
    enableRobotsTXT: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("enableRobotsTXT", "enablerobotstxt"),
    )
    environment: str | None = None
    # https://gohugo.io/configuration/front-matter/
    # Defines how Hugo extracts dates from frontmatter.
    # TODO: Define django-hugo data model for dates and set as default here.
    frontmatter: dict[str, Any] | None = None
    hasCjkLanguage: bool | None = Field(
        default=None, validation_alias=AliasChoices("hasCjkLanguage", "hascjklanguage")
    )
    HTTPcache: HTTPCache | None = Field(
        default=None, validation_alias=AliasChoices("HTTPcache", "httpcache")
    )
    # https://gohugo.io/configuration/imaging/
    # Controls image processing. Use defaults for now.
    imaging: dict[str, Any] | None = None
    languageCode: str = Field(
        default="en-us", validation_alias=AliasChoices("languageCode", "languagecode")
    )
    # https://gohugo.io/configuration/languages/
    # Future i18n, not implemented yet
    languages: dict[str, Any] | None = None
    mainSections: list[str] | None = Field(
        default=None, validation_alias=AliasChoices("mainSections", "mainsections")
    )
    markup: Markup | None = None
    mediaTypes: dict[str, MediaType] | None = Field(
        default=None, validation_alias=AliasChoices("mediaTypes", "mediatypes")
    )
    # TODO: Menu editor for django-hugo
    menus: dict | None = None
    # https://gohugo.io/configuration/minify/
    # TODO: Define django-hugo defaults for minification settings
    minify: dict[str, Any] | None = None
    # https://gohugo.io/configuration/module/
    # TODO: module config will encompass several django-hugo features.
    module: dict[str, Any] | None = None
    # https://gohugo.io/configuration/output-formats/
    # For future use, take defaults for now
    outputFormats: dict[str, OutputFormats] | None = Field(
        default=None, validation_alias=AliasChoices("outputFormats", "outputformats")
    )
    # https://gohugo.io/configuration/outputs/
    # For future use, take defaults for now
    outputs: dict[str, list[str]] | None = None
    # https://gohugo.io/configuration/page/
    # Default sort order for page collections, take defaults for now
    page: dict[str, Any] | None = None
    # https://gohugo.io/configuration/pagination/
    # We expose only pagerSize, but may support more in the future.
    pagination: Pagination | None = None
    params: dict = Field(default_factory=dict)
    # https://gohugo.io/configuration/permalinks/
    # For now we use a fixed configuration, but may expose this for customization later.
    permalinks: dict | None = None
    pluralizelistTitles: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("pluralizelistTitles", "pluralizelisttitles"),
    )
    # https://gohugo.io/configuration/privacy/
    # Future enhancement maybe
    privacy: dict[str, Any] | None = None
    # https://gohugo.io/configuration/related-content/
    # Future enhancement
    related: dict[str, Any] | None = None
    sectionPagesMenu: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sectionPagesMenu", "sectionpagesmenu"),
    )
    # https://gohugo.io/configuration/security/
    # TODO: Review security settings and define django-hugo defaults if needed
    security: dict[str, Any] | None = None
    # https://gohugo.io/configuration/segments/
    # Not needed until we hit scale
    segments: dict[str, Any] | None = None
    # Not used
    server: dict[str, Any] | None = None
    # https://gohugo.io/configuration/services/
    # TODO: Expose Disqus, Google Analytics, etc. as django-hugo features
    # TODO: Set RSS.Limit
    services: dict[str, Any] | None = None
    # https://gohugo.io/configuration/sitemap/
    # TODO: Expose sitemap changefreq?
    sitemap: dict[str, Any] | None = None
    summaryLength: int | None = Field(
        default=None, validation_alias=AliasChoices("summaryLength", "summarylength")
    )
    # https://gohugo.io/configuration/taxonomies/
    # TODO: Define and codify django-hugo data model for taxonomies
    taxonomies: dict | None = None
    theme: str | None = None
    timeZone: str | None = Field(
        default=None, validation_alias=AliasChoices("timeZone", "timezone")
    )
    title: str | None = None
    uglyURLs: bool | None = Field(
        default=None, validation_alias=AliasChoices("uglyURLs", "uglyurls")
    )

    model_config = ConfigDict(
        # Allow additional fields not explicitly defined. They will be stored in the
        # __pydantic_extra__ attribute, with no validation.
        extra="allow",
        json_encoders={HttpUrl: str},
    )


def toml_to_hugo_config(toml: str) -> HugoConfig:
    """
    Load and validate a Hugo configuration from a TOML string.

    Args:
        toml: A string containing the TOML configuration data.

    Returns:
        HugoConfig: The validated Hugo configuration model instance.

    Raises:
        tomli.TOMLDecodeError: If the TOML file is invalid.
        pydantic.ValidationError: If the data does not conform to HugoConfig.
    """
    data = tomli.loads(toml)
    return HugoConfig.model_validate(data)


def hugo_config_to_toml(config: HugoConfig) -> str:
    """
    Serialize a HugoConfig instance to a TOML string, including extra fields.

    Args:
        config (HugoConfig): The HugoConfig instance to serialize.

    Returns:
        str: The TOML string representation of the configuration.
    """

    # Get the model data as a dict, including extra fields
    data = config.model_dump(mode="json", exclude_unset=True, exclude_none=True)
    # Merge in __pydantic_extra__ if present (for extra fields)
    if hasattr(config, "__pydantic_extra__") and config.__pydantic_extra__:
        data.update(config.__pydantic_extra__)

    return tomli_w.dumps(data)
