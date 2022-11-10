from wdts.okapiwdt import OkapiWdt
from wdts.tfidfwdt import TfidfWdt
from wdts.wackywdt import WackyWdt
from wdts.defaultwdt import DefaultWdt
from indexing import Index
import struct
import sqlite3

class DiskIndexWriter(Index):
    def __init__(self):
        pass

    def writeIndex(self, index, path , docWeights_dict: dict, docLengthA, size_of_corpus: int):
        """Retrieve the vocabulary from the index, and loop through each term in the vocab list. Get the postings list
        for a term, then write the list to disk using the format mentioned below:
        dft(4-byte int), doc-id gap(4-byte int), Wdts(8-byte double each),tftd(4-byte int), positions gaps(4-byte int each)"""
        # Initialize path and open files to write
        pathDW = path + "/docWeights.bin"
        pathBin = path + "/postings.bin"
        pathDb = path + "/postings.db"
        pathDLA = path + "/docLengthA.bin"
        pathSC = path + "/sizeOfCorpus.bin"
        postingFile = open(pathBin, "wb")
        docWeightsFile = open(pathDW, "wb")
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
            bytePositionOfTerm = postingFile.tell()
            c.execute("INSERT INTO postings VALUES (:term, :pos)", {'term': key, 'pos': bytePositionOfTerm})
            conn.commit()
            # Writing dft
            postingFile.write(struct.pack("i", len(postingList)))
            previous_id = 0
            for posting in postingList:
                # Writing doc_id
                doc_id = posting.get_document_id() - previous_id
                postingFile.write(struct.pack("i", doc_id))
                previous_id = posting.get_document_id()

                tftd = len(posting.get_positions())

                # TODO: Writing Wdts of all methods -DSP
                # Write wdt(def)
                wdt1 = DefaultWdt.calculate_wdt(DefaultWdt, tftd)
                postingFile.write(struct.pack("d", wdt1))
                # Write wdt(tfidf)
                wdt2 = TfidfWdt.calculate_wdt(TfidfWdt, tftd)
                postingFile.write(struct.pack("d", wdt2))
                # Write wdt(okapi)
                wdt3 = OkapiWdt.calculate_wdt(OkapiWdt, tftd, docWeights_dict.get(doc_id)[1], docLengthA)
                postingFile.write(struct.pack("d", wdt3))
                # Write wdt(wacky)
                wdt4 = WackyWdt.calculate_wdt(WackyWdt, tftd, 0, avgTftd=docWeights_dict.get(doc_id)[3])
                postingFile.write(struct.pack("d", wdt4))


                # Writing tf-t,d
                postingFile.write(struct.pack("i", tftd))

                previous_pos = 0
                for pos in posting.get_positions():
                    # Writing positions
                    postingFile.write(struct.pack("i", pos - previous_pos))
                    previous_pos = pos

        for key, value in docWeights_dict.items():
            # Writing docWeights
            docWeightsFile.write(struct.pack("d", value[0]))
            # Writing docLengthD
            docWeightsFile.write(struct.pack("d", value[1]))
            # Writing byteSize
            docWeightsFile.write(struct.pack("d", value[2]))
            # Writing Avg(tftd)
            docWeightsFile.write(struct.pack("d", value[3]))

        # Writing docLengthA - single value
        docLengthAFile.write(struct.pack("d", docLengthA))

        # Writing size of corpus - single value
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
