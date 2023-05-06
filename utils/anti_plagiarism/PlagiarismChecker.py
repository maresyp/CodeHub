from dataclasses import dataclass
from enum import Enum
from collections import Counter


class PlagiarismMethod(Enum):
    """ Enum for plagiarism checking methods """
    BOW = 1  # Bag of words


@dataclass(frozen=True)
class PlagiarismResult:
    """ Class for storing plagiarism check result. """
    method: PlagiarismMethod
    percentage: float


class PlagiarismChecker:
    """ Class for checking plagiarism in the code """

    def __init__(self, reference_code: str) -> None:
        self.reference_code: str = reference_code

    def check_code(self, code: str, method: set[PlagiarismMethod]) -> set[PlagiarismResult]:
        """ Checks plagiarism in the code using all methods specified """
        results: set[PlagiarismResult] = set()

        if PlagiarismMethod.BOW in method:
            results.add(self.__check_bow(code))

        return results

    def __check_bow(self, code: str) -> PlagiarismResult:
        """ Checks plagiarism in the code using bag of words method """
        reference_words = Counter(self.reference_code.split())
        code_words = Counter(code.split())

        combined_words = reference_words + code_words

        bow1 = [reference_words[word] if word in reference_words else 0 for word in combined_words]
        bow2 = [code_words[word] if word in code_words else 0 for word in combined_words]

        print(bow1)
        print(bow2)


if __name__ == '__main__':
    checker = PlagiarismChecker("John likes to watch movies. Mary likes movies too.")
    print(checker.check_code("Mary also likes to watch football games.", {PlagiarismMethod.BOW}))
