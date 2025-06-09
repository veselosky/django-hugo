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
This module contains Pydantic models for Hugo's theme.toml file.
"""

from pathlib import Path

import tomli
from PIL import Image
from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    HttpUrl,
    field_validator,
    model_validator,
)
from typing_extensions import Self


class Author(BaseModel):
    name: str
    homepage: HttpUrl | None


class OriginalAuthor(BaseModel):
    author: str
    homepage: HttpUrl | None
    repo: HttpUrl | None


class ThemeMetadata(BaseModel):
    # Required fields from theme.toml
    name: str
    license: str
    licenselink: HttpUrl | None = None
    description: str
    homepage: HttpUrl

    # Optional fields from theme.toml
    demosite: HttpUrl | None = None
    tags: list[str] | None = []
    features: list[str] | None = []

    # Single-author or multi-author support
    author: Author | None = None
    authors: list[Author] | None = None

    # Optional “original” metadata
    original: OriginalAuthor | None = None

    # Paths to images (screenshot and thumbnail)
    screenshot: FilePath
    thumbnail: FilePath
    theme_dir: DirectoryPath

    @field_validator("screenshot", mode="after")
    @classmethod
    def check_screenshot_image(cls, path: Path) -> Path:
        """
        Validate that the screenshot image:
        - Exists
        - Has one of the allowed extensions (png, jpg, jpeg)
        - Has a 3:2 aspect ratio (width/height == 1.5)
        - Has minimum dimensions 1500×1000
        """
        ext = path.suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("Screenshot must be a PNG or JPG file")

        try:
            img = Image.open(path)
        except Exception as e:
            raise ValueError(f"Cannot open screenshot image: {e}")

        width, height = img.size
        if width < 1500 or height < 1000:
            raise ValueError(
                f"Screenshot must be at least 1500×1000 pixels (got {width}×{height})"
            )

        ratio = width / height
        if abs(ratio - 1.5) > 0.01:
            raise ValueError(
                f"Screenshot must have a 3:2 aspect ratio (width/height == 1.5), got {ratio:.2f}"
            )

        return path

    @field_validator("thumbnail", mode="after")
    @classmethod
    def check_thumbnail_image(cls, path: Path) -> Path:
        """
        Validate that the thumbnail image:
        - Exists
        - Has one of the allowed extensions (png, jpg, jpeg)
        - Has a 3:2 aspect ratio (width/height == 1.5)
        - Has minimum dimensions 900×600
        """
        ext = path.suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("Thumbnail must be a PNG or JPG file")

        try:
            img = Image.open(path)
        except Exception as e:
            raise ValueError(f"Cannot open thumbnail image: {e}")

        width, height = img.size
        if width < 900 or height < 600:
            raise ValueError(
                f"Thumbnail must be at least 900×600 pixels (got {width}×{height})"
            )

        ratio = width / height
        if abs(ratio - 1.5) > 0.01:
            raise ValueError(
                f"Thumbnail must have a 3:2 aspect ratio (width/height == 1.5), got {ratio:.2f}"
            )

        return path

    @model_validator(mode="after")
    def validate_author_fields(self) -> Self:
        """
        Ensure that either 'author' or 'authors' is provided (or neither,
        but not both) when theme.toml declares authorship.
        """
        author = self.author
        authors = self.authors

        if author and authors:
            raise ValueError(
                "Provide either 'author' (single) or 'authors' (list), not both."
            )
        return self


def load_theme_metadata(toml_path: str | Path) -> ThemeMetadata:
    """
    Load and validate Hugo theme metadata from a theme.toml file.

    Args:
        toml_path: Path to the theme.toml file (str or pathlib.Path).

    Returns:
        An instance of ThemeMetadata containing validated data.

    Raises:
        FileNotFoundError: If the theme.toml file or required images are not found.
        ValueError: If the theme.toml file is invalid or does not meet the required criteria.
        pydantic.ValidationError: If the data does not conform to the ThemeMetadata model.
    """
    toml_path = Path(toml_path)
    if not toml_path.is_file():
        raise FileNotFoundError(f"theme.toml not found at: {toml_path}")

    # Parse the TOML file
    with toml_path.open("rb") as f:
        data = tomli.load(f)

    data["theme_dir"] = str(toml_path.parent.resolve())
    images_dir = toml_path.parent / "images"
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    # docs say screenshot and thumbnail must be either .png or .jpg
    # Check which images exist. If we don't find at least one of each, raise an error.
    screenshot_png = images_dir / "screenshot.png"
    screenshot_jpg = images_dir / "screenshot.jpg"
    if not (screenshot_png.is_file() or screenshot_jpg.is_file()):
        raise FileNotFoundError(
            f"Screenshot image not found in {images_dir}. Expected screenshot.png or screenshot.jpg."
        )
    if screenshot_png.is_file():
        data["screenshot"] = str(screenshot_png.resolve())
    else:
        data["screenshot"] = str(screenshot_jpg.resolve())

    thumbnail_png = images_dir / "tn.png"
    thumbnail_jpg = images_dir / "tn.jpg"
    if not (thumbnail_png.is_file() or thumbnail_jpg.is_file()):
        raise FileNotFoundError(
            f"Thumbnail image not found in {images_dir}. Expected tn.png or tn.jpg."
        )
    if thumbnail_png.is_file():
        data["thumbnail"] = str(thumbnail_png.resolve())
    else:
        data["thumbnail"] = str(thumbnail_jpg.resolve())

    # Validate and instantiate the Pydantic model
    return ThemeMetadata.model_validate(data)
