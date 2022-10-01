from indexing.postings import Posting
from .querycomponent import QueryComponent


def _positional_intersect(p1: list[Posting], p2: list[Posting], k: int) -> list[Posting]:
    i = 0
    j = 0
    ans = []
    while i < len(p1) and j < len(p2):
        if p1[i].doc_id == p2[j].doc_id:
            # If the position matches according to k gap -> Add
            l = 0
            m = 0
            l1 = p1[i].position
            l2 = p2[j].position
            l3 = []
            while l < len(l1) and m < len(l2):
                if l + k == m:
                    # Add to l3
                    l3.append(l1[l])
                else:
                    if l + k < m:
                        l += 1
                    else:
                        m += 1

            if len(l3) is not 0:
                # Make a posting and add to ans
                newPosting = Posting(p1[i].doc_id)
                for position in l3:
                    newPosting.add_position(position)

                ans.append(newPosting)

            i += 1
            j += 1

        else:
            if p1[i].doc_id < p2[j].doc_id:
                i += 1
            else:
                j += 1

    return ans


class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: list[str]) -> object:
        self.terms = [s for s in terms]

    def get_postings(self, index) -> list[Posting]:
        # return None
        # TODO: program this method. Retrieve the postings for the individual terms in the phrase,
        # and positional merge them together.

        if len(self.terms) is 0:
            return []
        elif len(self.terms) is 1:
            return index.get_postings(self.terms[0])

        postingListForIndiTerm = []

        # Create a list of all Individual term posting
        for term in self.terms:
            postingListForIndiTerm.append(index.get_postings(term))

        position = 1
        answer = []

        while position < len(self.terms):
            if position == 1:
                # Perform positional intersect with first two postings
                answer = _positional_intersect(postingListForIndiTerm[0], postingListForIndiTerm[position], position)
                position += 1
            else:
                # Perform positional intersect for terms having position greater than 2
                answer = _positional_intersect(answer, postingListForIndiTerm[position], position)
                position += 1

        return answer

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
