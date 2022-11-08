from indexing import Index
from postings import Posting
import struct
import sqlite3


class DiskPositionalIndex(Index):
    def __init__(self, path):
        self.postingsList = []
        self.pathDB = path + "/postings.db"
        self.pathBin = path + "/postings.bin"
        self.pathLDBin = path + "/docWeights.bin"
        self.file = open(self.pathBin, "rb")

    def getPostings(self, term):
        conn = sqlite3.connect(self.pathDB)
        c = conn.cursor()
        c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        self.file.seek(termPos[0])
        file_contents = self.file.read()
        ptr = 0
        noOfDocs = struct.unpack("i", file_contents[ptr:ptr + 4])
        ptr += 4
        previous_docId = 0
        for i in range(noOfDocs[0]):
            docId = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            posting = Posting(docId[0] + previous_docId)
            previous_docId = docId[0]
            tftd = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            previous_poss = 0
            for j in range(tftd[0]):
                poss = struct.unpack("i", file_contents[ptr:ptr + 4])
                ptr += 4
                posting.add_position(poss[0] + previous_poss)
                previous_poss = poss[0]
            self.postingsList.append(posting)
        return self.postingsList
