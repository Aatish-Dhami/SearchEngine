from .index import Index
from .postings import Posting
import struct
import sqlite3


class DiskIndexWriter(Index):
    def __init__(self):
        pass

    def writeIndex(self, index, path):
        """Retrieve the vocabulary from the index, and loop through each term in the vocab list. Get the postings list
        for a term, then write the list to disk using our format: first dft, then a doc id gap, then tftd, then a bunch
        of position gaps, repeating."""

        newFile = open("postings.bin", "wb")
        conn = sqlite3.connect('postings.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE postings (
                    term text,
                    bytePos integer
                    )""")
        conn.commit()
        vocab = index.getVocabulary()

        for key, postingList in vocab.items():
            bytePositionOfTerm = newFile.tell()
            c.execute("INSERT INTO postings VALUES (:term, :pos)", {'term': key, 'pos': bytePositionOfTerm})
            conn.commit()
            # Writing dft
            newFile.write(struct.pack("i", len(postingList)))
            previous_id = 0
            for posting in postingList:
                # Writing doc_id
                newFile.write(struct.pack("i", posting.doc_id - previous_id))
                previous_id = posting.doc_id
                # Writing tf-t,d
                newFile.write(struct.pack("i", len(posting.position)))
                previous_pos = 0
                for pos in posting.position:
                    # Writing positions
                    newFile.write(struct.pack("i", pos - previous_pos))
                    previous_pos = pos