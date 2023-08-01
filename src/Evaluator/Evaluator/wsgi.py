"""
WSGI config for Evaluator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from Evaluator.wsgi import EvaluatorApplication
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Evaluator.settings")

application = get_wsgi_application()
#application = EvaluatorApplication(application)