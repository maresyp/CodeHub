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
        from Codes.models import Project
        while True:
            item = self.get()
            checked_code = Project.objects.get(id=item.reference_code_id)
            checker = PlagiarismChecker(checked_code.source_code)
            other_codes = Project.objects.all().exclude(id=checked_code.id, owner=checked_code.owner)
            for code in other_codes:
                result, *_ = checker.check_code(code.source_code, method={PlagiarismMethod.TFIDF})
                print(result)
                if checked_code.plagiarism_ratio < int(result.cosine_similarity * 100):
                    checked_code.plagiarism_ratio = int(result.cosine_similarity * 100)  # TODO: change data type
                    checked_code.save()

            self.task_done()
