from indexing.postings import Posting
from text.advancedtokenprocessor import AdvancedTokenProcessor
from .querycomponent import QueryComponent


class NearLiteral(QueryComponent):
    """
    A NearLiteral represents as [term1 NEAR/K term2]
    """

    def __init__(self, term1: str, term2: str, k: int):
        self.term1 = term1
        self.term2 = term2
        self.k = k

    def get_postings(self, index) -> list[Posting]:
        # TODO: Get postings by calling positionalIndex appropriately
        token_processor = AdvancedTokenProcessor()
        from queries.phraseliteral import _positional_intersect

        lsofpostings = []
        for i in range(self.k):
            lsofpostings.append(_positional_intersect(index.getPostings(token_processor.process_token(self.term1)[-1]),
                                  index.getPostings(token_processor.process_token(self.term2)[-1]),
                                  i+1))

        result = []
        position = 0
        while position < len(lsofpostings):
            r = 0
            i = 0
            positionPostings = lsofpostings[position]
            temp = []
            while r < len(result) and i < len(positionPostings):
                if result[r].doc_id == positionPostings[i].doc_id:
                    # Add to temp list
                    temp.append(Posting(result[r].doc_id))
                    r += 1
                    i += 1
                else:
                    if result[r].doc_id < positionPostings[i].doc_id:
                        temp.append(Posting(result[r].doc_id))
                        r += 1
                    else:
                        temp.append(Posting(positionPostings[i].doc_id))
                        i += 1

            while r < len(result):
                temp.append(Posting(result[r].doc_id))
                r += 1
            while i < len(positionPostings):
                temp.append(Posting(positionPostings[i].doc_id))
                i += 1

            result = temp
            position += 1

        return result

    def __str__(self) -> str:
        return "[" + self.term1 + " NEAR/" + self.k + " " + self.term2 + "]"
