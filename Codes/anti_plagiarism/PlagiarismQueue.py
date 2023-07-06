from queue import Queue
from typing import Self
import threading
from .PlagiarismChecker import PlagiarismChecker, PlagiarismMethod
import uuid
import time
from django.db.models import Q

class PlagiarismQueueEntry:
    """
    Represents a queue entry for plagiarism checks.

    Attributes:
        reference_code_id (uuid.UUID): The unique identifier of the code to be checked.
    """
    __slots__ = ['reference_code_id']

    def __init__(self, reference_code_id: uuid.UUID) -> None:
        """
        Initializes a new instance of the PlagiarismQueueEntry class.

        Args:
            reference_code_id (uuid.UUID): The unique identifier of the code to be checked.
        """
        self.reference_code_id = reference_code_id


class PlagiarismQueue(Queue):
    """
    Represents a queue for handling plagiarism checks.

    This class extends the built-in Queue class and uses threading to perform plagiarism checks in the background.

    Attributes:
        _instance (PlagiarismQueue): A singleton instance of the PlagiarismQueue.
    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        """
        Create a new instance of PlagiarismQueue or return the existing one.

        Returns:
            PlagiarismQueue: The singleton instance of the PlagiarismQueue.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes a new instance of the PlagiarismQueue class.

        Starts the worker and cleaner threads.
        """
        if self.__initialized:
            return
        self.__initialized: bool = True

        super().__init__(*args, **kwargs)
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()
        self.cleaner_thread = threading.Thread(target=self.cleaner, daemon=True)
        self.cleaner_thread.start()


    def put(self, item: PlagiarismQueueEntry, *args, **kwargs) -> None:
        """
        Add a new item to the queue.

        Args:
            item (PlagiarismQueueEntry): The item to add to the queue.
        """
        super().put(item)

    def worker(self) -> None:
        """
        Worker thread that continuously checks the queue for new items.

        For each item, retrieves the associated code and checks it against all other codes for plagiarism.

        If an exception occurs during the plagiarism check, the error is printed and the item is marked as done.
        """
        from Codes.models import Code
        while True:
            try:
                item = self.get()
                checked_code = Code.objects.get(id=item.reference_code_id)

                other_codes = Code.objects.exclude(
                    Q(id=item.reference_code_id) |
                    Q(project__owner=checked_code.project.owner)
                )
                # If there are no other codes to check, skip this code
                if not other_codes:
                    self.task_done()
                    continue
                checker = PlagiarismChecker(checked_code.source_code)
                highest_similarity: tuple[int, Code] = (0, other_codes.first())

                # Check all codes and find the one with highest similarity
                for code in other_codes:
                    result, *_ = checker.check_code(code.source_code, method={PlagiarismMethod.TFIDF})
                    if int(result.cosine_similarity * 100) > highest_similarity[0]:
                        highest_similarity = int(result.cosine_similarity * 100), code

                checked_code.plagiarism_ratio = highest_similarity[0]
                checked_code.plagiarized_from = highest_similarity[1]
                checked_code.save()

                self.task_done()
            except Exception as e:
                print(f'Error: {e} during plagiarism check')
                self.task_done()

    def cleaner(self) -> None:
        """
        Cleaner thread that runs in the background and periodically adds not checked codes to queue.

        This is needed because some codes may be skipped due to server malfunction.
        This way we can be sure that all codes will be checked.
        """
        from Codes.models import Code
        while True:
            try:
                time.sleep(60 * 60) # 1 hour
                codes = Code.objects.filter(plagiarized_from__isnull=True)
                print(f'Plagiarism cleaner thread: {len(codes)} codes to check')
                for code in codes:
                    self.put(PlagiarismQueueEntry(code.id))
            except Exception as e:
                print(f'Error: {e} inside plagiarism cleaner thread')