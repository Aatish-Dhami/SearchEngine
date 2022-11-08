from typing import Iterable
from .postings import Posting
from .index import Index


class SoundexIndex(Index):
    """Implements an SoundexIndex using Soundex Algorithm. Does not require anything prior to construction."""

    def __init__(self):
        """Constructs an empty SoundingIndex using dictionary."""
        self.vocab = {}

    def add_term(self, hashcode: str, doc_id: int):
        """Records that the given hash occurred in the given document ID."""
        if hashcode not in self.vocab:
            self.vocab[hashcode] = [Posting(doc_id)]
        else:
            # If docId is not same we append a new posting with different docID and first position encountered.
            if self.vocab.get(hashcode)[-1].doc_id != doc_id:
                self.vocab[hashcode].append(Posting(doc_id))
            # But If the docId is same we skip it...

    def getPostings(self, hashcode: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given hash."""
        return self.vocab.get(hashcode, [])

    def getVocabulary(self) -> Iterable[str]:
        """Returns list of vocabulary terms in a sorted manner"""
        return sorted(list(self.vocab.keys()))

    def getEntireVocab(self) -> dict:
        """Returns entire dictionary of vocabulary"""
        return self.vocab
