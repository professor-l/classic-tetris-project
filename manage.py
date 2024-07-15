#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Provided commands: https://docs.djangoproject.com/en/3.2/ref/django-admin/
# Custom commands can be found in classic_tetris_project/management/commands
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classic_tetris_project_django.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
