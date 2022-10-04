from indexing.postings import Posting
from text.advancedtokenprocessor import AdvancedTokenProcessor
from .querycomponent import QueryComponent

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str):
        self.term = term

    def get_postings(self, index) -> list[Posting]:
        # TODO: What to do if the term is hyphen - Done
        token_processor = AdvancedTokenProcessor()
        return index.getPostings(token_processor.process_token(self.term)[-1])

    def __str__(self) -> str:
        return self.term