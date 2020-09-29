"""
WSGI config for groupsw project.

It exposes the WSGI callable as a module-level variable named ``appointment``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groupsw.settings')

application = get_wsgi_application()
