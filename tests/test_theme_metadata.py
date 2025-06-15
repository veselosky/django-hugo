import logging
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from django_hugo.themes.config import load_theme_metadata

# Configure logging for the test module
logger = logging.getLogger(__name__)


def create_dummy_image(path: Path, width: int, height: int):
    """Create a dummy image with the specified dimensions and save it to the given path."""
    image = Image.new("RGB", (width, height), color="white")
    image.save(path)


class TestThemeMetadata(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        logger.debug(f"Temporary directory created at: {self.base_path}")

    def tearDown(self):
        self.temp_dir.cleanup()
        logger.debug(f"Temporary directory cleaned up: {self.base_path}")

    def create_dummy_files(self, screenshot_size, thumbnail_size):
        """Create dummy screenshot and thumbnail images in the temp directory."""
        img_path = self.base_path / "images"
        img_path.mkdir(parents=True, exist_ok=True)
        screenshot_path = img_path / "screenshot.png"
        thumbnail_path = img_path / "tn.png"
        create_dummy_image(screenshot_path, *screenshot_size)
        create_dummy_image(thumbnail_path, *thumbnail_size)
        logger.debug(f"Created dummy files: {screenshot_path}, {thumbnail_path}")
        return screenshot_path, thumbnail_path

    def write_toml(self, data: str, filename: str = "theme.toml") -> Path:
        """Write the provided TOML string to a file in the temp directory."""
        toml_path = self.base_path / filename
        with open(toml_path, "w", encoding="utf-8") as f:
            f.write(data)
        logger.debug(f"Wrote TOML data to: {toml_path}")
        return toml_path

    def test_valid_metadata_loading(self):
        # Create valid images: screenshot: 1500x1000, thumbnail: 900x600
        screenshot, thumbnail = self.create_dummy_files((1500, 1000), (900, 600))
        # Create a valid TOML string with relative paths
        toml_content = (
            "name = 'Test Theme'\n"
            "license = 'MIT'\n"
            "description = 'A description'\n"
            "homepage = 'http://example.com'\n"
            f"screenshot = '{screenshot.name}'\n"
            f"thumbnail = '{thumbnail.name}'\n"
        )
        toml_file = self.write_toml(toml_content)
        metadata = load_theme_metadata(toml_file)
        self.assertEqual(metadata.name, "Test Theme")
        self.assertEqual(metadata.license, "MIT")

    def test_invalid_author_fields(self):
        # Create valid images
        screenshot, thumbnail = self.create_dummy_files((1500, 1000), (900, 600))
        toml_content = (
            "name = 'Test Theme'\n"
            "license = 'MIT'\n"
            "description = 'A description'\n"
            "homepage = 'http://example.com'\n"
            f"screenshot = '{screenshot.name}'\n"
            f"thumbnail = '{thumbnail.name}'\n"
            "author = { name = 'Alice', homepage = 'http://alice.com' }\n"
            "authors = [ { name = 'Bob', homepage = 'http://bob.com' } ]\n"
        )
        toml_file = self.write_toml(toml_content)
        with self.assertRaises(ValueError):
            load_theme_metadata(toml_file)

    def test_invalid_screenshot_dimensions(self):
        # Create an invalid screenshot (dimensions too small) and a valid thumbnail
        screenshot, thumbnail = self.create_dummy_files((1000, 800), (900, 600))
        toml_content = (
            "name = 'Test Theme'\n"
            "license = 'MIT'\n"
            "description = 'A description'\n"
            "homepage = 'http://example.com'\n"
            f"screenshot = '{screenshot.name}'\n"
            f"thumbnail = '{thumbnail.name}'\n"
        )
        toml_file = self.write_toml(toml_content)
        with self.assertRaises(ValueError):
            load_theme_metadata(toml_file)

    def test_invalid_thumbnail_ratio(self):
        # Create a valid screenshot and an invalid thumbnail (wrong aspect ratio)
        # For thumbnail, width/height must be ~1.5; use 800x600 which gives 1.33...
        screenshot, thumbnail = self.create_dummy_files((1500, 1000), (800, 600))
        toml_content = (
            "name = 'Test Theme'\n"
            "license = 'MIT'\n"
            "description = 'A description'\n"
            "homepage = 'http://example.com'\n"
            f"screenshot = '{screenshot.name}'\n"
            f"thumbnail = '{thumbnail.name}'\n"
        )
        toml_file = self.write_toml(toml_content)
        with self.assertRaises(ValueError):
            load_theme_metadata(toml_file)


if __name__ == "__main__":
    unittest.main()
