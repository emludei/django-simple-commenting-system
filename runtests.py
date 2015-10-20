import sys

from django.conf import settings
from django.core.management import execute_from_command_line

from tests import tests_settings


if not settings.configured:
    settings.configure(tests_settings)


def runtests():
    argv = sys.argv[:1] + ['test'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
