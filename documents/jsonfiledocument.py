from io import StringIO
from pathlib import Path
from typing import Iterable
from .document import Document
import json


class JsonFileDocument(Document):
    """
    Represents a document that is saved as a Json file in the local file system.
    """

    def __init__(self, id: int, path: Path):
        super().__init__(id)
        self.path = path
        with open(self.path, 'r') as file:
            self.my_title = json.load(file).get('title')

    @property
    def getTitle(self) -> str:
        return self.my_title

    # returns TextIOWrapper
    def getContent(self) -> Iterable[str]:
        with open(self.path, 'r') as file:
            return StringIO(json.load(file).get('body'))

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'JsonFileDocument':
        """A factory method to create a JsonFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)
