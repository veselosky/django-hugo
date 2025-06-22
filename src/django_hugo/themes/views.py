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
import logging

from django.urls import reverse
from django.views.generic import ListView

from django_hugo.themes.models import HugoTheme

logger = logging.getLogger(__name__)


class ThemeBrowserView(ListView):
    """
    View a list of all available Hugo themes. If the `next` parameter is provided,
    the page will provide `select` buttons that link to that view providing the theme
    slug in the `theme` parameter. Note that this view does not necessarily need to
    be restricted to logged-in users, as you may want anonymous users to be able to see
    what themes are available. If you want it behind a login, you can subclass it or
    wrap it with `login_required`.

    The `next` parameter is the name of a Django View to be reversed.
    The `next_args` parameter may contain a comma-separated list of additional arguments
    for reverse.
    """

    model = HugoTheme
    template_name = "hugo/themes/theme_list.html"
    context_object_name = "themes"
    paginate_by = 64  # Number of themes per page
    allow_empty = True  # Allow empty theme list
    queryset = HugoTheme.objects.filter(active=True).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the next parameter to the context if it exists
        next_view = self.request.GET.get("next")
        if next_view:
            next_args = self.request.GET.get("next_args", "")
            next_args_list = next_args.split(",") if next_args else []
            try:
                next_url = reverse(next_view, args=next_args_list)
            except Exception:
                # If the reverse fails, log the error and set next_url to None
                logger.exception(
                    "Error reversing URL for view `%s` with args `%s`",
                    next_view,
                    next_args_list,
                )
                next_url = None
        else:
            next_url = None
        # Add the next URL to the context
        if next_url:
            context["next"] = next_view
            context["next_args"] = next_args
            context["next_url"] = next_url
        return context
