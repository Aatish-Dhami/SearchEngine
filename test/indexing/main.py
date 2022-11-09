import struct

from indexing import Index
from indexing import DiskIndexWriter
from indexing import Posting
import sqlite3

# vocab = {}
# p1 = Posting(2)
# p2 = Posting(5)
# p1.add_position(3)
# p1.add_position(7)
# p2.add_position(8)
# p2.add_position(11)
#
# p_list = []
# p_list.append(p1)
# p_list.append(p2)
# vocab['add'] = p_list
#
# p11 = Posting(4)
# p22 = Posting(8)
# p11.add_position(1)
# p11.add_position(2)
# p22.add_position(10)
# p22.add_position(12)
#
# p_list2 = []
# p_list2.append(p11)
# p_list2.append(p22)
# vocab['subtract'] = p_list2
#
# d1 = DiskIndexWriter()
# path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Milestone2"
# d1.writeIndex(vocab, path)
#
# conn = sqlite3.connect('postings.db')
# c = conn.cursor()
# c.execute("SELECT * FROM postings")
# print(c.fetchall())
# file = open("postings.bin", "rb")
# file.seek(0)
# file_contents = file.read()
# print(struct.unpack("9i", file_contents[:36]))

# print(struct.unpack_from("i", file_contents[36:44]))
postingsList = []
term = "subtract"
file = open("postings.bin", "rb")
conn = sqlite3.connect('postings.db')
c = conn.cursor()
c.execute("SELECT bytePos FROM postings WHERE term =:term", {'term': term})
termPos = c.fetchone()
print(type(termPos))
file.seek(termPos[0])
file_contents = file.read()
ptr = 0
noOfDocs = struct.unpack("i", file_contents[ptr:ptr+4])
ptr += 4
previous_docId = 0
for i in range(noOfDocs[0]):
    docId = struct.unpack("i", file_contents[ptr:ptr+4])
    ptr += 4
    posting = Posting(docId[0] + previous_docId)
    previous_docId = docId[0]
    tftd = struct.unpack("i", file_contents[ptr:ptr+4])
    ptr += 4
    previous_poss = 0
    for j in range(tftd[0]):
        poss = struct.unpack("i", file_contents[ptr:ptr+4])
        ptr += 4
        posting.add_position(poss[0] + previous_poss)
        previous_poss = poss[0]
    postingsList.append(posting)

for posting in postingsList:
    print(posting.doc_id)
    print(posting.position)