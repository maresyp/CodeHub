from django.core.management.base import BaseCommand, CommandParser
from Users.models import User, FavouritesTags
from Codes.models import Project, Code, Tag

from abc import ABC, abstractmethod
from faker import Faker
from faker.providers import BaseProvider
from typing import Iterable
import random
from pathlib import Path

class Command(BaseCommand):
    """
    A Django management command class that populates the database with users.

    :param BaseCommand: Inherits from Django's BaseCommand class.
    :type BaseCommand: class
    """
    help = 'Populates the database with the users'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Adds custom command arguments.

        :param parser: The command line parser.
        :type parser: CommandParser
        """
        parser.add_argument('amount', type=int, help='The number of users to be created')
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        """
        The function that executes the command logic.

        :param args: Command arguments.
        :type args: tuple
        :param kwargs: Command keyword arguments.
        :type kwargs: dict
        """
        available_tags: list[Tag] = Tag.objects.all()
        if not available_tags:
            raise ValueError("There are no tags in the database. Please add some tags first.")

        # check if every tag has a corresponding file
        to_remove: set[Tag] = set()
        for tag in available_tags:
            possible_files = list(Path("./code_snippets/").glob(f"*.{tag.name.lower()}.txt"))
            if not possible_files:
                to_remove.add(tag)
        available_tags = [tag for tag in available_tags if tag not in to_remove]

        user_generator = UserGenerator(available_tags)
        existing_emails = set(User.objects.values_list('email', flat=True))
        creations: int = 0

        requested = int(kwargs['amount'])
        if requested < 1:
            raise ValueError("Amount must be greater than 0.")

        print('Keep in mind that creation of Codes involves anti plagiarism checks')
        print('This can take a while. Do not interrupt the process.')

        while creations < requested:
            for data in user_generator.generate(requested - creations):
                if data['email'] in existing_emails:
                    print(f'User with email {data["email"]} already exists. Skipping')
                    continue
                else:
                    existing_emails.add(data['email'])

                # create user
                user = User.objects.create_user(
                    first_name=data['name'],
                    email=data['email'],
                    username=data['email'].split('@')[0],
                    password='default'
                )

                # create profile for given user
                profile = user.profile
                profile.city = 'Warsaw'
                profile.age = data['age']
                profile.bio = data['bio']
                profile.gender = data['gender']
                profile.social_github = r'https://github.com/maresyp/CodeHub'
                profile.save()

                # create project for given user
                project = Project.objects.create(
                    owner=user,
                    title=f'Project of {data["name"]}',
                    description=f'This is a mock project generated for {data["name"]}',
                )

                for tag, snippet in data['code_snippets'].items():
                    print(f'Creating {tag} code snippet for {data["name"]}')
                    for snip in snippet:
                        Code.objects.create(
                            project=project,
                            title=f'snippet.{tag.file_extension}',
                            description='This is a mock code snippet',
                            source_code=snip
                        )

                FavouritesTags.objects.create(
                    user_id=user,
                    tag_id=random.choice(available_tags),
                    value=10
                )

                creations += 1
                print(f'Created User with email {data["email"]}.')

        print(f'Created {creations} mock users.')

class Generator(ABC):
    """
    An abstract class for generating mock users.

    :param ABC: Inherits from Python's ABC (Abstract Base Class) class.
    :type ABC: class
    """

    @abstractmethod
    def generate(self, *args, **kwargs):
        """
        Abstract method for generating mock users.

        :param args: Command arguments.
        :type args: tuple
        :param kwargs: Command keyword arguments.
        :type kwargs: dict
        """
        raise NotImplementedError


class UserGenerator(Generator, BaseProvider):
    """
    A class for generating mock users.

    :param Generator: Inherits from the Generator abstract base class.
    :type Generator: class
    :param BaseProvider: Inherits from Faker's BaseProvider class.
    :type BaseProvider: class
    """

    def __init__(self, available_tags: list[Tag]):
        """
        Constructor for UserGenerator class.

        :param available_tags: A list of available tags.
        :type available_tags: list[Tag]
        """
        self.__faker = Faker()
        Faker.seed(2137)
        random.seed(2137)

        self.__tags: list[Tag] = available_tags

    def generate(self, amount: int = 1) -> Iterable[dict]:
        """
        Method for generating mock users.

        :param amount: The number of mock users to generate.
        :type amount: int
        :return: A generator yielding user data.
        :rtype: Iterable[dict]
        """
        if amount < 1:
            raise ValueError("Amount must be greater than 0.")

        for _ in range(amount):
            data = dict()
            data["gender"] = random.choice(["M", "F"])
            data["name"] = self.generate_name(data["gender"])
            data["email"] = self.generate_email(data["name"])
            data["pwd"] = self.generate_password()
            data["age"] = random.randint(18, 69)
            data["tags"] = random.sample(self.__tags, random.randint(1, 5))
            data["code_snippets"] = {tag: [self.generate_code_snippet(tag.name)] for tag in data["tags"]}
            data["bio"] = self.generate_bio()

            yield data

    def generate_name(self, gender: str) -> str:
        """
        Generates a random name based on the provided gender.

        :param gender: The gender of the name ("M" for male, "F" for female).
        :type gender: str
        :return: A random name.
        :rtype: str
        """
        if gender == "M":
            return f'{self.__faker.first_name_male()} {self.__faker.last_name_male()}'.lower()
        return f'{self.__faker.first_name_female()} {self.__faker.last_name_female()}'.lower()

    def generate_email(self, name: str) -> str:
        """
        Generates a random email address from a given name.

        :param name: The name of the user.
        :type name: str
        :return: A random email address.
        :rtype: str
        """
        return f'{name.replace(" ", ".")}{random.randint(0, 2137)}@{self.__faker.free_email_domain()}'.lower()

    def generate_password(self) -> str:
        """
        Generates a random password.

        :return: A random password.
        :rtype: str
        """
        return self.__faker.password(length=25, special_chars=True, digits=True, upper_case=True, lower_case=True)

    def generate_bio(self) -> str:
        """
        Generates a random bio.

        :return: A random bio.
        :rtype: str
        """
        return self.__faker.text(max_nb_chars=150)

    @staticmethod
    def generate_code_snippet(tag: str) -> str:
        """
        Acquires code snippet with a given tag.

        :param tag: The tag of the code snippet.
        :type tag: str
        :return: The content of the code snippet.
        :rtype: str
        :raise IndexError: If there are no matching files for the given tag.
        """
        file = None
        try:
            file = random.choice(list(Path("./code_snippets/").glob(f"*.{tag.lower()}.txt")))
        except IndexError as e:
            raise IndexError(f"No matching files for {tag} found.") from e

        with file.open('r') as f:
            return f.read()

