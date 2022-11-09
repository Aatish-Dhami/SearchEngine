from typing import Iterable
from indexing import Index
from indexing import Posting
import struct
import sqlite3
import numpy as np


class DiskPositionalIndex(Index):
    def __init__(self, path):
        self.pathDB = path + "/postings.db"
        self.pathBin = path + "/postings.bin"
        self.pathSDX = path + "/soundex.bin"
        self.pathSdxDB = path + "/soundex.db"
        self.file = open(self.pathBin, "rb")
        self.sfile = open(self.pathSDX, "rb")

    def getPostings(self, term) -> Iterable[Posting]:
        postingList = []
        conn = sqlite3.connect(self.pathDB)
        c = conn.cursor()
        c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        self.file.seek(termPos[0])
        file_contents = self.file.read()
        ptr = 0
        dft = struct.unpack("i", file_contents[ptr:ptr + 4])
        ptr += 4
        previous_docId = 0
        for i in range(dft[0]):
            docId = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            posting = Posting(docId[0] + previous_docId)
            previous_docId = posting.doc_id
            tftd = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            posting.set_wdt(tftd)
            previous_poss = 0
            for j in range(tftd[0]):
                poss = struct.unpack("i", file_contents[ptr:ptr + 4])
                ptr += 4
                posting.add_position(poss[0] + previous_poss)
                previous_poss = posting.position[-1]
            postingList.append(posting)
        conn.close()
        return postingList

    def getPostingsWithoutPositions(self, term) -> Iterable[Posting]:
        postingList = []
        conn = sqlite3.connect(self.pathDB)
        c = conn.cursor()
        c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        self.file.seek(termPos[0])
        file_contents = self.file.read()
        ptr = 0
        dft = struct.unpack("i", file_contents[ptr:ptr + 4])
        ptr += 4
        previous_docId = 0
        for i in range(dft[0]):
            docId = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            posting = Posting(docId[0] + previous_docId)
            previous_docId = posting.get_document_id()
            tftd = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            ptr += (tftd[0] * 4)
            postingList.append(posting)
        conn.close()
        return postingList

    def getPostingsSoundex(self, term) -> Iterable[Posting]:
        postingList = []
        conn = sqlite3.connect(self.pathSdxDB)
        c = conn.cursor()
        c.execute("SELECT bytePos FROM soundex WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        self.sfile.seek(termPos[0])
        file_contents = self.sfile.read()
        ptr = 0
        dft = struct.unpack("i", file_contents[ptr:ptr + 4])
        ptr += 4
        previous_docId = 0
        for i in range(dft[0]):
            docId = struct.unpack("i", file_contents[ptr:ptr + 4])
            ptr += 4
            posting = Posting(docId[0] + previous_docId)
            previous_docId = posting.get_document_id()
            postingList.append(posting)
        conn.close()
        return postingList

    def getVocabulary(self) -> list[str]:
        # get first 1000 terms
        conn = sqlite3.connect(self.pathDB)
        c = conn.cursor()
        c.execute("SELECT term FROM postings")
        list_of_tuple = c.fetchmany(1000)
        ans = []
        for t in list_of_tuple:
            ans.append(str(t))
        return ans

    def getWqt(self, term, size_of_corpus):
        conn = sqlite3.connect(self.pathDB)
        c = conn.cursor()
        c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
        termPos = c.fetchone()
        self.file.seek(termPos[0])
        file_contents = self.file.read()
        ptr = 0
        dft = struct.unpack("i", file_contents[ptr:ptr + 4])
        ptr += 4
        wqt = np.log(1 + (size_of_corpus / dft[0]))
        return wqt

