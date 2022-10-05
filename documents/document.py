from abc import ABC, abstractmethod
from typing import Iterable


class Document(ABC):
    """Represents an abstract grouping of content in a corpus."""

    def __init__(self, doc_id: int):
        self.id = doc_id

    @abstractmethod
    def getContent(self) -> Iterable[str]:
        """Gets an iterable sequence over the content of the document."""
        pass

    @abstractmethod
    def getTitle(self) -> str:
        """The title of the document, for displaying to the user."""
        pass

    # @abstractmethod
    # def getAuthor(self) -> str:
    #     """The Author of the document, for displaying to the user."""
    #     pass

    def __str__(self) -> str:
        return f"{self.getTitle} (ID {self.id})"
