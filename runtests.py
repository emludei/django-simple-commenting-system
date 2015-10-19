import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'app_comments',
                'HOST': '127.0.0.1',
                'PORT': '5432',
                'USER': 'app_comments',
                'PASSWORD': 'app_comments',
            }
        },
        ROOT_URLCONF='src.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.staticfiles',
            'django.contrib.contenttypes',
            'comments',
            'tests',
        ],
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['templates'],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        STATICFILES_DIRS=(
            os.path.join(BASE_DIR, "static"),
        ),
        STATIC_URL='/static/'
    )


def runtests():
    argv = sys.argv[:1] + ['test'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
