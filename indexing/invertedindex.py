from typing import Iterable
from .postings import Posting
from .index import Index


class InvertedIndex(Index):
    """Implements an InvertedIndex using a hash-map or dictionary. Does not require anything prior to construction."""

    def __init__(self):
        """Constructs an empty InvertedIndex using dictionary."""
        self.vocab = {}

    def add_term(self, term: str, doc_id: int, position: int):
        """Records that the given term occurred in the given document ID."""
        if term not in self.vocab:
            self.vocab[term] = [Posting(doc_id)]
            self.vocab[term][-1].add_position(position)
        else:
            # If docId is not same we append a new posting with different docID and first position encountered.
            if self.vocab.get(term)[-1].doc_id != doc_id:
                self.vocab[term].append(Posting(doc_id))
                self.vocab[term][-1].add_position(position)
            # But If the docId is same we do not skip it.. instead we add the position to the existing object
            else:
                self.vocab.get(term)[-1].add_position(position)

    def getPostings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        return self.vocab.get(term, [])

    def getVocabulary(self) -> Iterable[str]:
        return sorted(list(self.vocab.keys()))
