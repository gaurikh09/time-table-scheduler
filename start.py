import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'scheduler_project.settings'

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:8000'])
