import tempfile
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from django_hugo.themes.models import HugoTheme

# language: python


# Relative imports from the current package


class TestFindThemeFiles(TestCase):
    def setUp(self):
        # Create a temporary directory to simulate THEMES_ROOT
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)
        # Create structure:
        # root/theme1/theme.toml
        theme1 = self.root_path / "theme1"
        theme1.mkdir()
        (theme1 / "theme.toml").write_text("dummy content", encoding="utf-8")
        # root/sub/theme2/theme.toml
        sub_dir = self.root_path / "sub"
        sub_dir.mkdir()
        theme2 = sub_dir / "theme2"
        theme2.mkdir()
        (theme2 / "theme.toml").write_text("dummy content", encoding="utf-8")
        # Create an additional directory with no theme.toml
        (self.root_path / "empty_dir").mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_find_theme_files(self):
        # Call find_theme_files with our temporary directory
        from django_hugo.themes.actions import find_theme_files

        themes = find_theme_files(self.root_path)
        # Build expected paths set (resolved paths)
        expected = {
            str((self.root_path / "theme1" / "theme.toml").resolve()),
            str((self.root_path / "sub" / "theme2" / "theme.toml").resolve()),
        }
        result = {str(path.resolve()) for path in themes}
        self.assertEqual(result, expected)


class TestSyncThemes(TestCase):
    def setUp(self):
        # Create a temporary directory to simulate THEMES_ROOT
        self.temp_dir = tempfile.TemporaryDirectory()
        self.themes_root = Path(self.temp_dir.name)

        # Create a dummy theme directory with a theme.toml file
        self.dummy_theme_dir = self.themes_root / "dummy_theme"
        self.dummy_theme_dir.mkdir()
        self.theme_toml = self.dummy_theme_dir / "theme.toml"
        self.theme_toml.write_text("dummy toml", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def fake_load_theme_metadata(self, toml_path: Path):
        # Return a fake theme object with required attributes
        return SimpleNamespace(
            name=f"Test Theme {uuid.uuid4()}", description="Dummy Description"
        )

    def test_sync_creates_new_theme(self):
        from django_hugo.themes.actions import sync_themes

        # Ensure no themes exist initially
        HugoTheme.objects.all().delete()

        with override_settings(HUGO_THEMES_ROOT=self.themes_root):
            with patch(
                "django_hugo.themes.actions.load_theme_metadata",
                side_effect=self.fake_load_theme_metadata,
            ):
                sync_themes(self.themes_root)

                themes = HugoTheme.objects.all()
                self.assertEqual(themes.count(), 1)
                theme = themes.first()
                self.assertTrue(theme.name.startswith("Test Theme"))
                self.assertEqual(theme.toml_path, str(self.theme_toml.resolve()))
                self.assertEqual(theme.description, "Dummy Description")
                self.assertTrue(theme.active)

    def test_sync_deactivates_missing_theme(self):
        from django_hugo.themes.actions import sync_themes

        # Create an existing theme in the db that isn't available in file system after sync
        HugoTheme.objects.all().delete()

        # Add an extra theme with a path not present in the file system
        fake_path = str((self.themes_root / "nonexistent" / "theme.toml").resolve())
        extra_theme = HugoTheme.objects.create(
            name="Extra Theme",
            toml_path=fake_path,
            description="Extra Description",
            active=True,
        )
        with patch(
            "django_hugo.themes.actions.load_theme_metadata",
            side_effect=self.fake_load_theme_metadata,
        ):
            sync_themes(self.themes_root)

            # Refresh from db
            extra_theme.refresh_from_db()
            self.assertFalse(extra_theme.active)
