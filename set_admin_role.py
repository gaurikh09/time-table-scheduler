from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler_project.settings')
django.setup()

User = get_user_model()
username = input("Enter username to make admin: ")
try:
    user = User.objects.get(username=username)
    user.role = 'admin'
    user.save()
    print(f"✓ {username} is now an admin!")
except User.DoesNotExist:
    print(f"✗ User '{username}' not found")
