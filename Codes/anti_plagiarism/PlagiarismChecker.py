from dataclasses import dataclass
from enum import Enum
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import math
import numpy as np


class PlagiarismMethod(Enum):
    """ Enum for plagiarism checking methods """
    BOW = 1  # Bag of words
    TFIDF = 2  # TF-IDF


@dataclass(frozen=True)
class PlagiarismResult:
    """ Class for storing plagiarism check result. """
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
        """ Judge if the result is plagiarized """
        if self.jaccard_similarity > jaccard_threshold:
            return True
        if self.euclidian_distance > euclidian_threshold:
            return True
        if self.cosine_similarity > cosine_threshold:
            return True

        return False


class PlagiarismChecker:
    """ Class for checking plagiarism in the code """

    def __init__(self, reference_code: str) -> None:
        self.reference_code: str = reference_code

    def check_code(self, code: str, method: set[PlagiarismMethod]) -> set[PlagiarismResult]:
        """ Checks plagiarism in the code using all methods specified """
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
        """ Returns bag of words for reference code and tested code """
        reference_words = Counter(self.reference_code.split())
        code_words = Counter(code.split())

        combined_words = reference_words + code_words
        bow1 = [reference_words[word] if word in reference_words else 0 for word in combined_words]
        bow2 = [code_words[word] if word in code_words else 0 for word in combined_words]

        return bow1, bow2

    @staticmethod
    def __jaccard_similarity(reference_words: set[str], code_words: set[str]) -> float:
        """ Calculates Jaccard similarity between two sets of words """
        intersection = reference_words & code_words
        union = reference_words | code_words

        return len(intersection) / len(union)

    @staticmethod
    def __normalized_euclidian_distance(x: np.ndarray, y: np.ndarray) -> float:
        """ Calculates Euclidian distance """
        dist = math.sqrt(sum(pow(a - b, 2) for a, b in zip(x, y)))
        # normalization to 0-1 range
        return 1 / math.exp(dist)

    @staticmethod
    def __cosine_similarity(x: np.ndarray, y: np.ndarray) -> float:
        """ Calculates cosine similarity """
        dot_product = sum(a * b for a, b in zip(x, y))
        magnitude = math.sqrt(sum(pow(a, 2) for a in x)) * math.sqrt(sum(pow(b, 2) for b in y))
        return dot_product / magnitude

    def __create_bow_embeddings(self, code: str) -> tuple[np.ndarray, np.ndarray]:
        """ Creates embeddings for reference code and tested code """
        bow = CountVectorizer(lowercase=False).fit_transform([self.reference_code, code]).toarray()
        return bow[0], bow[1]

    def __create_tfid_embeddings(self, code: str) -> tuple[np.ndarray, np.ndarray]:
        """ Creates embeddings for reference code and tested code """
        embeddings = TfidfVectorizer(lowercase=False).fit_transform([self.reference_code, code]).toarray()
        return embeddings[0], embeddings[1]

    def __whitespace_analysis(self, code: str) -> float:
        """ Calculates whitespace similarity between two codes """
        pass


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
