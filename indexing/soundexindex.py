from typing import Iterable, List
from .postings import Posting
from .index import Index


class SoundexIndex(Index):
    """Implements an SoundexIndex using Soundex Algorithm. Does not require anything prior to construction."""

    def __init__(self):
        """Constructs an empty SoundingIndex using dictionary."""
        self.vocab = {}

    def add_term(self, hashcode: str):
        """Records that the given hash occurred in the given document ID."""
        pass

    def getPostings(self, hashcode: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given hash."""
        return self.vocab.get(hashcode, [])

    def getVocabulary(self) -> Iterable[str]:
        return sorted(list(self.vocab.keys()))