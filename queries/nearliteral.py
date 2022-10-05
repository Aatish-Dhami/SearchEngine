from indexing.postings import Posting
from text.advancedtokenprocessor import AdvancedTokenProcessor
from .querycomponent import QueryComponent
from queries import phraseliteral
from phraseliteral import _positional_intersect

class NearLiteral(QueryComponent):
    """
    A NearLiteral represents a single term in a subquery.
    """

    def __init__(self, term1 : str, term2 : str, k):
        self.term1 = term1
        self.term2 = term2
        self.k = k

    def get_postings(self, index) -> list[Posting]:
        # TODO: Get postings by calling positionalIndex appropriately
        answer = _positional_intersect(self.term1, self.term2, self.k)

    def __str__(self) -> str:
        return self.term1