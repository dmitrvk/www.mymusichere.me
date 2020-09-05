# Licensed under the MIT License

"""WSGI config for mymusichere project.

It exposes the WSGI callable as a module-level variable named `application`.
"""

import os

from django.core import wsgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mymusichere.settings')

application = wsgi.get_wsgi_application()
