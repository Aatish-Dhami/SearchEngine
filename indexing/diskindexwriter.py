from indexing import Index
from indexing import Posting
import struct
import sqlite3
import os


class DiskIndexWriter(Index):
    def __init__(self):
        pass

    def writeIndex(self, index, path: str, ld_dict: dict):
        """Retrieve the vocabulary from the index, and loop through each term in the vocab list. Get the postings list
        for a term, then write the list to disk using our format: first dft, then a doc id gap, then tftd, then a bunch
        of position gaps, repeating."""

        pathLDBin = path + "/docWeights.bin"
        pathBin = path + "/postings.bin"
        pathDb = path + "/postings.db"
        newFile = open(pathBin, "wb")
        ldFile = open(pathLDBin, "wb")
        conn = sqlite3.connect(pathDb)
        c = conn.cursor()
        c.execute("""DROP TABLE IF EXISTS postings""")
        conn.commit()
        c.execute("""CREATE TABLE postings (
                    term text,
                    bytePos integer
                    )""")
        conn.commit()

        # Writing ldDict
        for key, value in ld_dict.items():
            ldFile.write(struct.pack("d", value))

        voc = index.getEntireVocab()
        for key, postingList in voc.items():
            bytePositionOfTerm = newFile.tell()
            c.execute("INSERT INTO postings VALUES (:term, :pos)", {'term': key, 'pos': bytePositionOfTerm})
            conn.commit()
            # Writing dft
            newFile.write(struct.pack("i", len(postingList)))
            previous_id = 0
            for posting in postingList:
                # Writing doc_id
                newFile.write(struct.pack("i", posting.get_document_id() - previous_id))
                previous_id = posting.get_document_id()
                # Writing tf-t,d
                newFile.write(struct.pack("i", len(posting.get_positions())))
                previous_pos = 0
                for pos in posting.get_positions():
                    # Writing positions
                    newFile.write(struct.pack("i", pos - previous_pos))
                    previous_pos = pos

    def writeSoundexIndex(self, index, path):
        pathSDX = path + "/soundex.bin"
        pathSdxDB = path + "/soundex.db"
        newFile = open(pathSDX, "wb")
        conn = sqlite3.connect(pathSdxDB)
        c = conn.cursor()
        c.execute("""DROP TABLE IF EXISTS soundex""")
        conn.commit()
        c.execute("""CREATE TABLE soundex (
                        term text,
                        bytePos integer
                        )""")
        conn.commit()

        voc = index.getEntireVocab()

        for key, postingList in voc.items():
            bytePositionOfTerm = newFile.tell()
            c.execute("INSERT INTO soundex VALUES (:term, :pos)", {'term': key, 'pos': bytePositionOfTerm})
            conn.commit()
            # Writing dft
            newFile.write(struct.pack("i", len(postingList)))
            previous_id = 0
            for posting in postingList:
                # Writing doc_id
                newFile.write(struct.pack("i", posting.get_document_id() - previous_id))
                previous_id = posting.get_document_id()
