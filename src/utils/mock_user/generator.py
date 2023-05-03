from abc import ABC, abstractmethod
from faker import Faker
from faker.providers import BaseProvider
from typing import Iterable
import random
from pathlib import Path
class Generator(ABC):
    """ Abstract class for generating mock users. """

    @abstractmethod
    def generate(self, *args, **kwargs):
        """ Abstract method for generating mock users. """
        raise NotImplementedError

class UserGenerator(Generator, BaseProvider):
    """ Class for generating mock users. """

    def __init__(self, available_tags: list[str] | None = None):
        """ Constructor for UserGenerator class. """
        self.__faker = Faker()
        Faker.seed(2137)
        random.seed(2137)

        if available_tags is None:
            self.__tags = ["Python", "C", "Cpp", "Java", "Javascript"]
        else:
            self.__tags: list[str] = available_tags # type: ignore

    def generate(self, amount: int = 1) -> Iterable[dict]:
        """ Method for generating mock users. """
        if amount < 1:
            raise ValueError("Amount must be greater than 0.")

        for _ in range(amount):
            data = dict()
            data["gender"] = random.choice(["M", "F"])
            data["name"] = self.generate_name(data["gender"])
            data["email"] = self.generate_email(data["name"])
            data["pwd"] = self.generate_password()
            data["age"] = random.randint(18, 69)
            data["tags"] = random.sample(self.__tags, random.randint(1, len(self.__tags)))
            data["code_snippets"] = {tag: [self.generate_code_snippet(tag) for tag in data["tags"]] for tag in data["tags"]}
            data["bio"] = self.generate_bio()

            yield data

    def generate_name(self, gender: str) -> str:
        """ Method for generating a random name. """
        if gender == "M":
            return f'{self.__faker.first_name_male()} {self.__faker.last_name_male()}'
        return f'{self.__faker.first_name_female()} {self.__faker.last_name_female()}'

    def generate_email(self, name: str) -> str:
        """ Method for generating a random email from given name. """
        return f'{name.replace(" ", ".")}{random.randint(0, 2137)}@{self.__faker.free_email_domain()}'

    def generate_password(self) -> str:
        """ Method for generating a random password. """
        return self.__faker.password(length=25, special_chars=True, digits=True, upper_case=True, lower_case=True)

    def generate_bio(self) -> str:
        """ Method for generating a random bio. """
        return self.__faker.text(max_nb_chars=150)

    def generate_code_snippet(self, tag: str) -> str:
        """ Method for acquiring code snippet with given tag """
        file = None
        try:
            file = random.choice(list(Path("./code_snippets/").glob(f"*.{tag.lower()}.txt")))
        except IndexError as e:
            print(f"There are no {tag} files in code_snippets directory.")
            print("Please run src/utils/async_crawler.py to download some.")
            raise e

        with file.open('r') as f:
            return f.read()


if __name__ == "__main__":
    user_generator = UserGenerator()
    for user in user_generator.generate(amount=50):
        print(user)