from queue import Queue
from typing import Self
import threading
from .PlagiarismChecker import PlagiarismChecker, PlagiarismMethod, PlagiarismResult
import uuid


class PlagiarismQueueEntry:
    __slots__ = ['reference_code_id']

    def __init__(self, reference_code_id: uuid.UUID) -> None:
        self.reference_code_id = reference_code_id


class PlagiarismQueue(Queue):
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def put(self, item: PlagiarismQueueEntry, *args, **kwargs) -> None:
        super().put(item)

    def worker(self) -> None:
        from Codes.models import Code
        while True:
            item = self.get()
            checked_code = Code.objects.get(id=item.reference_code_id)
            checker = PlagiarismChecker(checked_code.source_code)
            other_codes = Code.objects.all().exclude(id=checked_code.id, owner=checked_code.owner)

            highest_similarity = 0
            for code in other_codes:
                result, *_ = checker.check_code(code.source_code, method={PlagiarismMethod.TFIDF})
                print(result)
                if int(result.cosine_similarity * 100) > highest_similarity:
                    highest_similarity = int(result.cosine_similarity * 100)

            checked_code.plagiarism_ratio = highest_similarity
            checked_code.save()

            self.task_done()
