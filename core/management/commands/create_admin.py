import os
from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', '')
        email = os.environ.get('ADMIN_EMAIL', '')

        if not password:
            self.stdout.write('ADMIN_PASSWORD not set, skipping admin creation.')
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(f'Admin user "{username}" already exists — role updated.')
        else:
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                role='admin',
            )
            self.stdout.write(f'Admin user "{username}" created successfully.')
