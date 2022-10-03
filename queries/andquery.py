from .querycomponent import QueryComponent
from indexing import Index, Posting
from queries import querycomponent


class AndQuery(QueryComponent):
    def __init__(self, components: list[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index) -> list[Posting]:
        result = []
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
        # intersecting the resulting postings.
        result = self.components[0].get_postings(index)

        position = 1
        while position < len(self.components):
            r = 0
            i = 0
            positionPostings = self.components[position].get_postings(index)
            temp = []
            while r < len(result) and i < len(positionPostings):
                if result[r].doc_id == positionPostings[i].doc_id:
                    # Add to temp list and increment
                    temp.append(Posting(result[r].doc_id))
                    r += 1
                    i += 1
                else:
                    if result[r].doc_id < positionPostings[i].doc_id:
                        r += 1
                    else:
                        i += 1
            result = temp

        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))
