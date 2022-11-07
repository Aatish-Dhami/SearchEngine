import struct

from indexing import Index
from indexing import DiskIndexWriter
from indexing import Posting
import sqlite3

vocab = {}
p1 = Posting(2)
p2 = Posting(5)
p1.add_position(3)
p1.add_position(7)
p2.add_position(8)
p2.add_position(11)

p_list = []
p_list.append(p1)
p_list.append(p2)
vocab['add'] = p_list

p11 = Posting(4)
p22 = Posting(8)
p11.add_position(1)
p11.add_position(2)
p22.add_position(10)
p22.add_position(12)

p_list2 = []
p_list2.append(p11)
p_list2.append(p22)
vocab['subtract'] = p_list2

d1 = DiskIndexWriter()
path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Milestone2"
d1.writeIndex(vocab, path)

conn = sqlite3.connect('postings.db')
c = conn.cursor()
c.execute("SELECT * FROM postings")
print(c.fetchall())
file = open("postings.bin", "rb")
# file_contents = file.read()
file.seek(0)
file_contents = file.read()
print(struct.unpack("9i", file_contents[:36]))

# print(struct.unpack_from("i", file_contents[36:44]))