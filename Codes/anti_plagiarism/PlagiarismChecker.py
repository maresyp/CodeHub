from dataclasses import dataclass
from enum import Enum
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import math
import numpy as np


class PlagiarismMethod(Enum):
    """Enum representing the methods used for plagiarism checking.

    Attributes:
        BOW: A constant for the Bag of Words method.
        TFIDF: A constant for the TF-IDF method.
    """
    BOW = 1  # Bag of words
    TFIDF = 2  # TF-IDF


@dataclass(frozen=True)
class PlagiarismResult:
    """Data class for storing plagiarism check results.

    Attributes:
        method (PlagiarismMethod): The method used for checking.
        jaccard_similarity (float): The Jaccard similarity index.
        euclidian_distance (float): The Euclidian distance between document embeddings.
        cosine_similarity (float): The cosine similarity between document embeddings.
    """
    method: PlagiarismMethod
    jaccard_similarity: float
    euclidian_distance: float
    cosine_similarity: float

    def judge_result(
            self,
            jaccard_threshold: float = 0.8,
            euclidian_threshold: float = 0.8,
            cosine_threshold: float = 0.8
    ) -> bool:
        """Determines whether the document is likely plagiarized based on the calculated metrics.

        Args:
            jaccard_threshold (float): The threshold value for the Jaccard similarity index.
            euclidian_threshold (float): The threshold value for the Euclidian distance.
            cosine_threshold (float): The threshold value for the cosine similarity.

        Returns:
            bool: True if any metric exceeds its threshold, indicating possible plagiarism.
        """
        if self.jaccard_similarity > jaccard_threshold:
            return True
        if self.euclidian_distance > euclidian_threshold:
            return True
        if self.cosine_similarity > cosine_threshold:
            return True

        return False


class PlagiarismChecker:
    """A class to check for plagiarism in code.

    Attributes:
        reference_code (str): The code against which other code will be checked.
    """

    def __init__(self, reference_code: str) -> None:
        """Initializes a PlagiarismChecker with a reference code.

        Args:
            reference_code (str): The code to check against.
        """
        self.reference_code: str = reference_code

    def check_code(self, code: str, method: set[PlagiarismMethod]) -> set[PlagiarismResult]:
        """
        Checks for plagiarism in the given code using the specified methods.

        Args:
            code (str): The code to check.
            method (set[PlagiarismMethod]): The set of methods to use for checking.

        Returns:
            set[PlagiarismResult]: A set of PlagiarismResults for each method used.
        """
        results: set[PlagiarismResult] = set()
        embeddings = []

        if PlagiarismMethod.BOW in method:
            bow = self.__create_bow_embeddings(code)
            embeddings.append((PlagiarismMethod.BOW, bow))
        if PlagiarismMethod.TFIDF in method:
            tfidf = self.__create_tfid_embeddings(code)
            embeddings.append((PlagiarismMethod.TFIDF, tfidf))

        # calculate similarity for each method
        jaccard = self.__jaccard_similarity(set(self.reference_code.split()), set(code.split()))
        for embedding in embeddings:
            method, emb = embedding

            euclidian = self.__normalized_euclidian_distance(emb[0], emb[1])
            cosine = self.__cosine_similarity(emb[0], emb[1])

            results.add(PlagiarismResult(method, jaccard, euclidian, cosine))

        return results

    def __construct_bow(self, code: str) -> tuple[list[int], list[int]]:
        """
        Returns bag of words for reference code and tested code.

        Args:
            code (str): The code to test.

        Returns:
            tuple[list[int], list[int]]: Two lists representing bag of words vectors for reference and test code.
        """
        reference_words = Counter(self.reference_code.split())
        code_words = Counter(code.split())

        combined_words = reference_words + code_words
        bow1 = [reference_words[word] if word in reference_words else 0 for word in combined_words]
        bow2 = [code_words[word] if word in code_words else 0 for word in combined_words]

        return bow1, bow2

    @staticmethod
    def __jaccard_similarity(reference_words: set[str], code_words: set[str]) -> float:
        """
        Calculates Jaccard similarity between two sets of words.

        Args:
            reference_words (set[str]): Words from the reference code.
            code_words (set[str]): Words from the tested code.

        Returns:
            float: Jaccard similarity score.
        """
        intersection = reference_words & code_words
        union = reference_words | code_words

        return len(intersection) / len(union)

    @staticmethod
    def __normalized_euclidian_distance(x: np.ndarray, y: np.ndarray) -> float:
        """
        Calculates Euclidian distance between two vectors.

        Args:
            x (np.ndarray): First vector.
            y (np.ndarray): Second vector.

        Returns:
            float: Normalized Euclidian distance.
        """
        dist = math.sqrt(sum(pow(a - b, 2) for a, b in zip(x, y)))
        # normalization to 0-1 range
        return 1 / math.exp(dist)

    @staticmethod
    def __cosine_similarity(x: np.ndarray, y: np.ndarray) -> float:
        """
        Calculates cosine similarity between two vectors.

        Args:
            x (np.ndarray): First vector.
            y (np.ndarray): Second vector.

        Returns:
            float: Cosine similarity score.
        """
        dot_product = sum(a * b for a, b in zip(x, y))
        magnitude_x = math.sqrt(sum(pow(a, 2) for a in x))
        magnitude_y = math.sqrt(sum(pow(b, 2) for b in y))
        if magnitude_x == 0.0 or magnitude_y == 0.0:
            return 0.0
        else:
            return dot_product / (magnitude_x * magnitude_y)

    def __create_bow_embeddings(self, code: str) -> tuple[np.ndarray, np.ndarray]:
        """
        Creates Bag of Words embeddings for reference code and tested code.

        Args:
            code (str): The code to test.

        Returns:
            tuple[np.ndarray, np.ndarray]: Two numpy arrays representing Bag of Words vectors for reference and test code.
        """
        bow = CountVectorizer(lowercase=False).fit_transform([self.reference_code, code]).toarray()
        return bow[0], bow[1]

    def __create_tfid_embeddings(self, code: str) -> tuple[np.ndarray, np.ndarray]:
        """
        Creates TF-IDF embeddings for reference code and tested code.

        Args:
            code (str): The code to test.

        Returns:
            tuple[np.ndarray, np.ndarray]: Two numpy arrays representing TF-IDF vectors for reference and test code.
        """
        embeddings = TfidfVectorizer(lowercase=False).fit_transform([self.reference_code, code]).toarray()
        return embeddings[0], embeddings[1]


if __name__ == '__main__':
    doc1 = """import asyncio
    import httpx
    from bs4 import BeautifulSoup
    from pathlib import Path
    from html.parser import HTMLParser
    from utils.async_crawler import AsyncCrawler

    class PasteParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.source_name = None
    """

    doc2 = """
    imt main() {
        int a = 5;
        int b = 6;
        int c = a + b;
        printf("%d", c);

    }
    """

    checker = PlagiarismChecker(doc1)
    result = checker.check_code(doc2, {PlagiarismMethod.TFIDF, PlagiarismMethod.BOW})
    for r in result:
        print(f"{r.judge_result()} {r}")
