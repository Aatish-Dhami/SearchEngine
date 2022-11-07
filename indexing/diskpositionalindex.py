from indexing import Index
from postings import Posting
import struct
import sqlite3


class DiskPositionalIndex(Index):
    def __init__(self):
        self.postingsList = []

    def getPostings(self, term):
        file = open("postings.bin", "rb")
        conn = sqlite3.connect('postings.db')
        c = conn.cursor()
        c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        print(type(termPos))
        file.seek(termPos[0])
        file_contents = file.read()
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
