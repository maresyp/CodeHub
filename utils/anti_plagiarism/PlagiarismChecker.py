from dataclasses import dataclass
from enum import Enum
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import math


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
            bow = self.__get_bow(code)
            for b in bow:
                print(b)

        print(f"jaccard: {self.__jaccard_similarity(set(self.reference_code.split()), set(code.split()))}")

        embeddings = self.__create_embeddings(code)

        return results

    def __get_bow(self, code: str) -> tuple[list[int], list[int]]:
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
    def __normalized_euclidian_distance(x, y) -> float:
        """ Calculates Euclidian distance """
        dist = math.sqrt(sum(pow(a-b, 2) for a, b in zip(x, y)))
        # normalization to 0-1 range
        return 1 / math.exp(dist)

    @staticmethod
    def __cosine_similarity(x, y) -> float:
        """ Calculates cosine similarity """
        dot_product = sum(a*b for a, b in zip(x, y))
        magnitude = math.sqrt(sum(pow(a, 2) for a in x)) * math.sqrt(sum(pow(b, 2) for b in y))
        return dot_product / magnitude

    def __create_embeddings(self, code: str) -> tuple[list[int], list[int]]:
        """ Creates embeddings for reference code and tested code """
        vect = CountVectorizer(lowercase=False)
        # create bag of words for reference code and tested code
        embeddings = vect.fit_transform([self.reference_code, code])
        print(vect.get_feature_names_out())
        print(embeddings.toarray())
        print(f"euclidian: {self.__normalized_euclidian_distance(embeddings.toarray()[0], embeddings.toarray()[1])}")
        print(f"cosine: {self.__cosine_similarity(embeddings.toarray()[0], embeddings.toarray()[1])}")

        tfidf = TfidfVectorizer(lowercase=False).fit_transform([self.reference_code, code])
        print(f"euclid tfidf: {self.__normalized_euclidian_distance(tfidf.toarray()[0], tfidf.toarray()[1])}")
        print(f"cosine tfidf: {self.__cosine_similarity(tfidf.toarray()[0], tfidf.toarray()[1])}")

        samples, features = tfidf
        return samples, features


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
    print(checker.check_code(doc2, {PlagiarismMethod.BOW}))
