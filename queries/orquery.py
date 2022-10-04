from .querycomponent import QueryComponent
from indexing import Index, Posting

from queries import querycomponent


class OrQuery(QueryComponent):
    def __init__(self, components: list[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index) -> list[Posting]:
        result = []
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        # merging the resulting postings.

        position = 0
        while position < len(self.components):
            r = 0
            i = 0
            positionPostings = self.components[position].get_postings(index)
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

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
