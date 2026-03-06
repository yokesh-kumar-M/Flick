"""
Create a default admin user and sample users.
Usage: python manage.py seed_users
"""
from django.core.management.base import BaseCommand
from authentication.models import FlickUser


class Command(BaseCommand):
    help = 'Seeds the auth database with admin and sample users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding users...')

        # Admin user
        if not FlickUser.objects.filter(username='admin').exists():
            admin = FlickUser(
                username='admin',
                email='admin@flick.io',
                display_name='Admin',
                is_admin=True,
            )
            admin.set_password('Admin123!')
            admin.save()
            self.stdout.write('  Admin user created (admin / Admin123!)')

        # Sample users
        sample_users = [
            {'username': 'alice', 'email': 'alice@flick.io', 'display_name': 'Alice', 'password': 'Alice123!', 'favorite_genre': 'Sci-Fi'},
            {'username': 'bob', 'email': 'bob@flick.io', 'display_name': 'Bob', 'password': 'Bobby123!', 'favorite_genre': 'Action'},
            {'username': 'charlie', 'email': 'charlie@flick.io', 'display_name': 'Charlie', 'password': 'Charlie123!', 'favorite_genre': 'Comedy'},
        ]

        for u_data in sample_users:
            if not FlickUser.objects.filter(username=u_data['username']).exists():
                user = FlickUser(
                    username=u_data['username'],
                    email=u_data['email'],
                    display_name=u_data['display_name'],
                    favorite_genre=u_data.get('favorite_genre', ''),
                )
                user.set_password(u_data['password'])
                user.save()
                self.stdout.write("  User '%s' created" % u_data['username'])

        self.stdout.write(self.style.SUCCESS('Users seeded successfully!'))
