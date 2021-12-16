import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

application = get_wsgi_application()

from django.core.management import call_command

if __name__ == "__main__":
    result = call_command('tgbot', plain=True)
    sys.exit(result)
