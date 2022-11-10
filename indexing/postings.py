import numpy as np


class Posting:
    """A Posting encapsulates a document ID associated with a search query component."""

    def __init__(self, doc_id: int):
        self.doc_id = doc_id
        self.position = []
        self.wdt = []  # default, tfidf, okapi, wacky in order

    def add_position(self, position):
        self.position.append(position)

    def get_document_id(self):
        return self.doc_id

    def get_positions(self):
        return self.position

    def get_wdt(self):
        # returns the wdt list of that term in the document
        return self.wdt

    def add_wdt(self, value):
        # add the value of wdt for this particular posting for its term
        self.wdt.append(value)
