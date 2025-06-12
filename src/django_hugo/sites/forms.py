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
Forms used by the Hugo Sites views.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from django_hugo.sites.models import HugoSite


class HugoSiteForm(forms.ModelForm):
    """
    Form for creating and updating Hugo sites. In addition to the model fields, this
    form also includes fields to populate the hugo.toml configuration.
    """

    title = forms.CharField(
        max_length=255,
        required=True,
        label=_("Site Title"),
        help_text=_("Title of the Hugo site, used in the site configuration"),
    )
    base_url = forms.URLField(
        required=False,
        label=_("Base URL"),
        help_text=_(
            "Full base URL for the Hugo site, starting with 'http' and ending with '/'"
        ),
    )
    copyright = forms.CharField(
        max_length=255,
        required=False,
        label=_("Copyright <year> by:"),
        help_text=_("Copyright notice for the Hugo site, used in the site footer"),
    )

    class Meta:
        model = HugoSite
        fields = [
            "name",
            "slug",
            "title",
            "description",
            "copyright",
            "base_url",
            "theme",
            "archived",
        ]
        labels = {
            "name": _("Site Name"),
            "slug": _("Short Name"),
            "description": _("Description"),
            "theme": _("Theme"),
            "archived": _("Archived"),
        }
        help_texts = {
            "name": _("Administrative name, not used in the site itself"),
            "slug": _(
                "Short name, used for folder and file names. "
                "Only letters, numbers, and hyphens are allowed (no spaces)."
            ),
            "description": _("Optional description of the Hugo site"),
            "theme": _("Theme to use for this Hugo site"),
            "archived": _("Indicates if the site is archived and not actively used"),
        }


class HugoListSiteForm(forms.Form):
    """
    Form for listing Hugo sites. This form is used to filter and search for sites.
    """

    search = forms.CharField(
        required=False,
        label=_("Search"),
        help_text=_("Search for sites by name or slug"),
    )
    archived = forms.BooleanField(
        required=False,
        label=_("Show Archived"),
        help_text=_("Include archived sites in the list"),
    )

    def clean(self):
        cleaned_data = super().clean()
        # Additional validation logic can be added here if needed
        return cleaned_data
