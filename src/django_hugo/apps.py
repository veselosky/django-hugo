from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class DjangoHugoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_hugo"
    verbose_name = _("Django Hugo")

    def ready(self):
        # Ensure that the app is registered before accessing its models
        if not apps.ready:
            return

        # Import the signals and tasks to ensure they are registered
        from . import signals, tasks  # noqa: F401
