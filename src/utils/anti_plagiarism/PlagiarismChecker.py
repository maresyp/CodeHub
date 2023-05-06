from dataclasses import dataclass


@dataclass(frozen=True)
class PlagiarismResult:
    """ Class for storing plagiarism check result. """
    code_id: int
    is_plagiarized: bool
    percentage: float


class PlagiarismChecker:
    """ Class for checking plagiarism in the code """

    def __init__(self) -> None:
        pass

    def check(self, code_id: int) -> set[PlagiarismResult]:
        """ Method for checking plagiarism in the code """
        pass
