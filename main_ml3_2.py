from numpy.dual import norm

from indexing import DiskPositionalIndex
from text.advancedtokenprocessor import AdvancedTokenProcessor
from documents import DirectoryCorpus
from text import EnglishTokenStream
import os
import math
import struct
import numpy as np


madi_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/MADISON"
jay_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/JAY"
hami_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/HAMILTON"
disp_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/DISPUTED"

# Objects of corpus
madison_index = DiskPositionalIndex(madi_path)
jay_index = DiskPositionalIndex(jay_path)
hamilton_index = DiskPositionalIndex(hami_path)
disputed_index = DiskPositionalIndex(disp_path)

# size of corpus
mfile = open("/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/MADISON"
             "/sizeOfCorpus.bin", "rb")
jfile = open("/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/JAY/sizeOfCorpus"
             ".bin", "rb")
hfile = open("/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/federalist-papers/HAMILTON"
             "/sizeOfCorpus.bin", "rb")
madison_size = struct.unpack("i", mfile.read()[0:4])[0]
jay_size = struct.unpack("i", jfile.read()[0:4])[0]
hamilton_size = struct.unpack("i", hfile.read()[0:4])[0]

# retrieve vocab lists
madison_vocab = madison_index.getEntireVocabulary()
jay_vocab = jay_index.getEntireVocabulary()
hamilton_vocab = hamilton_index.getEntireVocabulary()
disputed_vocab = disputed_index.getEntireVocabulary()
total_vocab = madison_vocab + jay_vocab + hamilton_vocab + disputed_vocab
total_vocab = [*set(total_vocab)]
total_vocab = sorted(total_vocab)[1:]

# get Madison postings
madison_postings = {}
for term in madison_vocab:
    postings = madison_index.getPostings(term)
    madison_postings[term] = postings

# get Jay postings
jay_postings = {}
for term in jay_vocab:
    postings = jay_index.getPostings(term)
    jay_postings[term] = postings

# get Hamilton postings
hamilton_postings = {}
for term in hamilton_vocab:
    postings = hamilton_index.getPostings(term)
    hamilton_postings[term] = postings

# get disputer postings
disputed_postings = {}
for term in disputed_vocab:
    postings = disputed_index.getPostings(term)
    disputed_postings[term] = postings

# calculate Ns
N = hamilton_size + madison_size + jay_size


def load_directory(path):
    if os.listdir(path)[0].endswith('.json'):
        dd = DirectoryCorpus.load_json_directory(path, ".json")
        fTyp = 1
    else:
        dd = DirectoryCorpus.load_text_directory(path, ".txt")
        fTyp = 0
    return dd, fTyp


def get_document_vectors(class_order):

    path_dict = {
        0: madi_path,
        1: jay_path,
        2: hami_path,
        3: disp_path
    }

    vocab_dict = {
        0: madison_vocab,
        1: jay_vocab,
        2: hamilton_vocab,
        3: disputed_vocab
    }

    pathDW = path_dict[class_order] + "/docWeights.bin"
    dwfile = open(pathDW, "rb")

    # For each document in path
    tkn_processor = AdvancedTokenProcessor()
    dd, fType = load_directory(path_dict[class_order])

    class_vectors = []
    for d in dd:
        vector_array = []
        document_vocab = []
        stream = EnglishTokenStream(d.getContent())
        for position, s in enumerate(stream):
            processed_token_list = tkn_processor.process_token(s)
            document_vocab.append(processed_token_list[-1])

        for vocab in total_vocab:
            if vocab in document_vocab:
                # Put docWeights which sum of wdt^2 divide by Ld
                dwfile.seek(32 * d.id)
                file_contents = dwfile.read(8)
                docWeights = struct.unpack("d", file_contents)[0]
                vector_array.append(docWeights)
            else:
                vector_array.append(0)
        class_vectors.append([dd.get_document(d.id).getTitle , np.array(vector_array)])

    return class_vectors


def update_neighbors(k_n, cosine_value, doc_name):
    if len(k_n) < 5:
        k_n.append([doc_name, cosine_value])
        # return k_n
    else:
        if cosine_value > k_n[0][1]:
            k_n[4] = k_n[3]
            k_n[3] = k_n[2]
            k_n[2] = k_n[1]
            k_n[1] = k_n[0]
            k_n[0] = [doc_name, cosine_value]
        elif cosine_value > k_n[1][1]:
            k_n[4] = k_n[3]
            k_n[3] = k_n[2]
            k_n[2] = k_n[1]
            k_n[1] = [doc_name, cosine_value]
        elif cosine_value > k_n[2][1]:
            k_n[4] = k_n[3]
            k_n[3] = k_n[2]
            k_n[2] = [doc_name, cosine_value]
        elif cosine_value > k_n[3][1]:
            k_n[4] = k_n[3]
            k_n[3] = [doc_name, cosine_value]
        elif cosine_value > k_n[4][1]:
            k_n[4] = [doc_name, cosine_value]

    return k_n


if __name__ == "__main__":
    madison_vdocs = get_document_vectors(0)
    jay_vdocs = get_document_vectors(1)
    hami_vdocs = get_document_vectors(2)
    disp_vdocs = get_document_vectors(3)

    # Predict
    pred = {}
    for vdoc in disp_vdocs:
        k_neighbors = []

        for mdocs in madison_vdocs:
            cosine = np.dot(vdoc[1], mdocs[1])/(norm(vdoc[1])*norm(mdocs[1]))
            k_neighbors = update_neighbors(k_neighbors, cosine, mdocs[0])

        for jdocs in jay_vdocs:
            cosine = np.dot(vdoc[1], jdocs[1])/(norm(vdoc[1])*norm(jdocs[1]))
            k_neighbors = update_neighbors(k_neighbors, cosine, jdocs[0])

        for hdocs in hami_vdocs:
            cosine = np.dot(vdoc[1], hdocs[1])/(norm(vdoc[1])*norm(hdocs[1]))
            k_neighbors = update_neighbors(k_neighbors, cosine, hdocs[0])

        pred[vdoc[0]] = k_neighbors

    for key, value in pred.items():
        print(key, end=": ")
        print(value)