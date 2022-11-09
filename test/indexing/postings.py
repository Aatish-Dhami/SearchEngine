class Posting:
    """A Posting encapsulates a document ID associated with a search query component."""

    def __init__(self, doc_id: int):
        self.doc_id = doc_id
        self.position = []

    def add_position(self, position):
        self.position.append(position)
