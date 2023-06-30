from django.core.management.base import BaseCommand
from Users.models import User, Tag

admins = {
    'admin': {
        'first_name': 'admin',
        'username': 'admin',
        'password': 'admin',
        'email': 'admin@o2.pl'
    },
}

users = {
    'maresyp': {
        'first_name': 'maresyp',
        'username': 'maresyp',
        'password': 'maresyp',
        'email': 'maresyp@o2.pl'
    },
    'miro': {
        'first_name': 'miro',
        'username': 'miro',
        'password': 'miro',
        'email': 'miro@o2.pl'
    }
}

tags = {
    'python': 'py',
    'java': 'java',
    'c++': 'cpp',
    'c#': 'csharp',
    'javascript': 'js',
    'html': 'html',
    'css': 'css',
    'php': 'php',
    'sql': 'sql',
    'ruby': 'ruby',
    'go': 'go',
    'swift': 'swift',
    'kotlin': 'kotlin',
    'r': 'r',
    'typescript': 'ts',
    'scala': 'scala',
    'rust': 'rust',
    'matlab': 'matlab',
    'perl': 'perl',
    'assembly': 'asm',
    'bash': 'bash',
    'powershell': 'powershell',
    'objective-c': 'objc',
    'groovy': 'groovy',
    'visual basic': 'vb',
    'dart': 'dart',
    'elixir': 'elixir',
    'haskell': 'haskell',
    'lua': 'lua',
    'julia': 'julia',
    'cobol': 'cobol',
    'fortran': 'fortran',
    'lisp': 'lisp',
    'pascal': 'pascal',
}

class Command(BaseCommand):
    help = 'Populates the database with default users, tags and other needed stuff'

    def handle(self, *args, **kwargs):
        # create default admins
        for key, value in admins.items():
            try:
                User.objects.create_superuser(**value)
                print(f'Created super-user with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} super-user.')

        # create default users
        for key, value in users.items():
            try:
                User.objects.create_user(**value)
                print(f'Created user with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} user.')

        # create default tags
        for key, value in tags.items():
            try:
                Tag.objects.create(name=key, file_extension=value)
                print(f'Created tag with parameters: {key}, {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} tag.')

