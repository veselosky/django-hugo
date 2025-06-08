# django-hugo
A web front-end for the Hugo static site generator

The following settings are **required**:

- `HUGO_PATH` -- The path to the hugo binary. It will try to use what is given, but will give a warning if the Hugo version is less than 0.146.1 as somethemes may not work with older versions.
- `HUGO_THEMES_ROOT` -- Path to the directory where you keep Hugo themes. You are responsible for placing themes in this directory. Will error if no themes are present.
- `HUGO_SITES_ROOT` -- Path to the directory where Django-Hugo will place the sites it creates. Must be writable by the user running the app.
