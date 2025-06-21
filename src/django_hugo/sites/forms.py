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

from django_hugo.models import HugoSite, HugoTheme


class HugoSiteForm(forms.ModelForm):
    """
    Form for creating and updating Hugo sites. In addition to the model fields, this
    form also includes fields to populate the hugo.toml configuration.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For now allow select a theme. We'll implement theme browser soon.
        self.fields["theme"].queryset = HugoTheme.objects.filter(active=True)

    class Meta:
        model = HugoSite
        fields = [
            "name",
            "slug",
            "title",
            "description",
            "copyright",
            "base_url",
            "pager_size",
            "enable_emoji",
            "enable_robots",
            "theme",
        ]
        labels = {
            "name": _("Site Name"),
            "slug": _("Short Name"),
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


class HugoSiteListForm(forms.Form):
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
