from indexing import Index
from indexing import Posting
import struct
import sqlite3
import os


class DiskIndexWriter(Index):
    def __init__(self):
        pass

    def writeIndex(self, index, path , docWeights_dict: dict, docLengthD_dict: dict, docLengthA, size_of_corpus: int, bytesize: int):
        """Retrieve the vocabulary from the index, and loop through each term in the vocab list. Get the postings list
        for a term, then write the list to disk using the format mentioned below:
        dft(4-byte int), doc-id gap(4-byte int), Wdts(8-byte double each),tftd(4-byte int), positions gaps(4-byte int each)"""
        # Initialize path and open files to write
        pathDW = path + "/docWeights.bin"
        pathBin = path + "/postings.bin"
        pathDb = path + "/postings.db"
        pathDLD = path + "/docLengthD.bin"
        pathDLA = path + "/docLengthA.bin"
        pathSC = path + "/sizeOfCorpus.bin"
        newFile = open(pathBin, "wb")
        docWeightsFile = open(pathDW, "wb")
        docLengthDFile = open(pathDLD, "wb")
        docLengthAFile = open(pathDLA, "wb")
        sizeOfCorpusFile = open(pathSC, "wb")

        # Create table postings
        conn = sqlite3.connect(pathDb)
        c = conn.cursor()
        c.execute("""DROP TABLE IF EXISTS postings""")
        conn.commit()
        c.execute("""CREATE TABLE postings (
                    term text,
                    bytePos integer
                    )""")
        conn.commit()

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
                # TODO: Writing Wdts of all methods -DSP
                # Writing tf-t,d
                newFile.write(struct.pack("i", len(posting.get_positions())))
                previous_pos = 0
                for pos in posting.get_positions():
                    # Writing positions
                    newFile.write(struct.pack("i", pos - previous_pos))
                    previous_pos = pos

        # Writing docWeights
        for key, value in docWeights_dict.items():
            docWeightsFile.write(struct.pack("d", value))

        # Writing docLengthD
        for key, value in docLengthD_dict.items():
            docLengthDFile.write(struct.pack("d", value))

        # Writing docLengthA
        docLengthAFile.write(struct.pack("d", docLengthA))

        # Writing size of corpus
        sizeOfCorpusFile.write(struct.pack("i", size_of_corpus))

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
