import itertools

from indexing import DiskPositionalIndex
from text.advancedtokenprocessor import AdvancedTokenProcessor
from documents import DirectoryCorpus
from text import EnglishTokenStream
import os
import math
import struct


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


def get_tStar():
    # process hamilton
    non_hamilton_docs = madison_size + jay_size
    hamilton_itc = {}
    for term in hamilton_vocab:
        # n00 - Number of documents not in hamilton and does not contain term
        # -- A - get nos of docs from madison with term
        if term in madison_postings:
            a = len(madison_postings[term])
        else:
            a = 0
        # -- B - get nos of docs from jay with term
        if term in jay_postings:
            b = len(jay_postings[term])
        else:
            b = 0
        # -- non hamilton total docs - (A + B)
        n00 = non_hamilton_docs - a - b
        # n10 - Not in hamilton and does contain term
        n10 = a + b
        # n01 - In hamilton and does not contain term
        n01 = hamilton_size - len(hamilton_postings[term])
        # n11 - In hamilton and contains term
        n11 = len(hamilton_postings[term])
        # n1x = n10 + n11
        n1x = n10 + n11
        # n0x = n01 + n00
        n0x = n01 + n00
        # nx0 = n00 + n10
        nx0 = n00 + n10
        # nx1 = n01 + n11
        nx1 = n01 + n11

        # calculate itc for this term in this class
        try:
            t1 = ((n11 / N) * math.log2((N * n11) / (n1x * nx1)))
        except:
            t1 = -math.inf
        try:
            t2 = ((n10 / N) * math.log2((N * n10) / (n1x * nx0)))
        except:
            t2 = -math.inf
        try:
            t3 = ((n01 / N) * math.log2((N * n01) / (n0x * nx1)))
        except:
            t3 = -math.inf
        try:
            t4 = ((n00 / N) * math.log2((N * n00) / (n0x * nx0)))
        except:
            t4 = -math.inf

        sum = t1 + t2 + t3 + t4
        if sum < 0:
            hamilton_itc[term] = 0
        else:
            hamilton_itc[term] = t1 + t2 + t3 + t4

    # process jay
    non_jay_docs = madison_size + hamilton_size
    jay_itc = {}
    for term in jay_vocab:
        # n00 - Number of documents not in jay and does not contain term
        # -- A - get nos of docs from jay with term
        if term in madison_postings:
            a = len(madison_postings[term])
        else:
            a = 0
        # -- B - get nos of docs from jay with term
        if term in hamilton_postings:
            b = len(hamilton_postings[term])
        else:
            b = 0
        # -- non jay total docs - (A + B)
        n00 = non_jay_docs - a - b
        # n10 - Not in jay and does contain term
        n10 = a + b
        # n01 - In jay and does not contain term
        n01 = jay_size - len(jay_postings[term])
        # n11 - In jay and contains term
        n11 = len(jay_postings[term])
        # n1x = n10 + n11
        n1x = n10 + n11
        # n0x = n01 + n00
        n0x = n01 + n00
        # nx0 = n00 + n10
        nx0 = n00 + n10
        # nx1 = n01 + n11
        nx1 = n01 + n11

        # calculate itc for this term in this class
        try:
            t1 = ((n11 / N) * math.log2((N * n11) / (n1x * nx1)))
        except:
            t1 = -math.inf
        try:
            t2 = ((n10 / N) * math.log2((N * n10) / (n1x * nx0)))
        except:
            t2 = -math.inf
        try:
            t3 = ((n01 / N) * math.log2((N * n01) / (n0x * nx1)))
        except:
            t3 = -math.inf
        try:
            t4 = ((n00 / N) * math.log2((N * n00) / (n0x * nx0)))
        except:
            t4 = -math.inf

        sum = t1 + t2 + t3 + t4
        if sum < 0:
            jay_itc[term] = 0
        else:
            jay_itc[term] = t1 + t2 + t3 + t4

    # process madison
    non_madison_docs = jay_size + hamilton_size
    madison_itc = {}
    for term in madison_vocab:
        # n00 - Number of documents not in jay and does not contain term
        # -- A - get nos of docs from jay with term
        if term in jay_postings:
            a = len(jay_postings[term])
        else:
            a = 0
        # -- B - get nos of docs from jay with term
        if term in hamilton_postings:
            b = len(hamilton_postings[term])
        else:
            b = 0
        # -- non jay total docs - (A + B)
        n00 = non_madison_docs - a - b
        # n10 - Not in jay and does contain term
        n10 = a + b
        # n01 - In jay and does not contain term
        n01 = madison_size - len(madison_postings[term])
        # n11 - In jay and contains term
        n11 = len(madison_postings[term])
        # n1x = n10 + n11
        n1x = n10 + n11
        # n0x = n01 + n00
        n0x = n01 + n00
        # nx0 = n00 + n10
        nx0 = n00 + n10
        # nx1 = n01 + n11
        nx1 = n01 + n11

        # calculate itc for this term in this class
        try:
            t1 = ((n11 / N) * math.log2((N * n11) / (n1x * nx1)))
            # t1 = ((n11 / N) * math.log(((N * n11) / (n1x * nx1)), 2))
        except:
            # t1 = -math.inf
            t1 = 0
        try:
            t2 = ((n10 / N) * math.log2((N * n10) / (n1x * nx0)))
            # t2 = ((n10 / N) * math.log(((N * n10) / (n1x * nx0)), 2))
        except:
            # t2 = -math.inf
            t2 = 0
        try:
            t3 = ((n01 / N) * math.log2((N * n01) / (n0x * nx1)))
            # t3 = ((n01 / N) * math.log(((N * n01) / (n0x * nx1)), 2))
        except:
            # t3 = -math.inf
            t3 = 0
        try:
            t4 = ((n00 / N) * math.log2((N * n00) / (n0x * nx0)))
            # t4 = ((n00 / N) * math.log(((N * n00) / (n0x * nx0)), 2))
        except:
            # t4 = -math.inf
            t4 = 0

        sum = t1 + t2 + t3 + t4
        if sum < 0:
            madison_itc[term] = 0
        else:
            madison_itc[term] = t1 + t2 + t3 + t4

    sorted_madison_itc = dict(sorted(madison_itc.items(), key=lambda item: item[1], reverse=True))
    sorted_jay_itc = dict(sorted(jay_itc.items(), key=lambda item: item[1], reverse=True))
    sorted_hamilton_itc = dict(sorted(hamilton_itc.items(), key=lambda item: item[1], reverse=True))
    ans = get_first_fifty(sorted_hamilton_itc, sorted_jay_itc, sorted_madison_itc)
    ans_sorted = dict(sorted(ans.items(), key=lambda item: item[1], reverse=True))
    return ans_sorted


def get_first_fifty(sorted_hamilton_itc, sorted_jay_itc, sorted_madison_itc):
    ans = {}
    m = 0
    j = 0
    h = 0

    while len(ans) < 50:
        current_max_val = max(list(sorted_hamilton_itc.items())[h][1], list(sorted_madison_itc.items())[m][1], list(sorted_jay_itc.items())[j][1])
        if list(sorted_hamilton_itc.items())[h][1] == current_max_val:
            if list(sorted_hamilton_itc.items())[h][0] not in ans:
                ans[list(sorted_hamilton_itc.items())[h][0]] = list(sorted_hamilton_itc.items())[h][1]
            h += 1
        elif list(sorted_madison_itc.items())[m][1] == current_max_val:
            if list(sorted_madison_itc.items())[m][0] not in ans:
                ans[list(sorted_madison_itc.items())[m][0]] = list(sorted_madison_itc.items())[m][1]
            m += 1
        else:
            if list(sorted_jay_itc.items())[j][0] not in ans:
                ans[list(sorted_jay_itc.items())[j][0]] = list(sorted_jay_itc.items())[j][1]
            j += 1

    return ans


def calc_laplace(t_itc):
    for key in t_itc.keys():
        value = []
        # Class madison
        if key in madison_postings:
            value.append([len(madison_postings[key]), -1])
        else:
            value.append([0, -1])

        ptici = ((value[-1][0]+1) / (len(madison_vocab) + 50))
        value[-1][1] = ptici
        # Class jay
        if key in jay_postings:
            value.append([len(jay_postings[key]), -1])
        else:
            value.append([0, -1])

        ptici = ((value[-1][0]+1) / (len(jay_vocab) + 50))
        value[-1][1] = ptici

        # Class hamilton
        if key in hamilton_postings:
            value.append([len(hamilton_postings[key]), -1])
        else:
            value.append([0, -1])

        ptici = ((value[-1][0]+1) / (len(hamilton_vocab) + 50))
        value[-1][1] = ptici

        t_itc[key] = value

    return t_itc


def load_directory(path):
    if os.listdir(path)[0].endswith('.json'):
        dd = DirectoryCorpus.load_json_directory(path, ".json")
        fTyp = 1
    else:
        dd = DirectoryCorpus.load_text_directory(path, ".txt")
        fTyp = 0
    return dd, fTyp


def get_cd(ptc_tab, class_order):
    # For each document in disputed
    tkn_processor = AdvancedTokenProcessor()
    dd, fType = load_directory(disp_path)
    # Calculate Cd for each document for all 3 classes
    cds = {}
    for d in dd:
        stream = EnglishTokenStream(d.getContent())

        ptc_sum = 0
        # Calculate ptc sum
        for position, s in enumerate(stream):
            processed_token_list = tkn_processor.process_token(s)
            if processed_token_list[-1] in ptc_tab.keys():
                ptc_sum += math.log10(ptc_tab[processed_token_list[-1]][class_order][1])

        # calc cd now
        if class_order == 0:
            cd_for_this_d = math.log10(madison_size / N) + ptc_sum
        elif class_order == 1:
            cd_for_this_d = math.log10(jay_size / N) + ptc_sum
        else:
            cd_for_this_d = math.log10(hamilton_size / N) + ptc_sum

        # append cd
        cds[dd.get_document(d.id).getTitle] = cd_for_this_d
        # cds[d.id] = cd_for_this_d
    return cds


if __name__ == "__main__":
    t_star_itc = get_tStar()

    # madison, jay, hamilton in order
    ptc_table = calc_laplace(t_star_itc)

    # get cd for all docs each class
    cds_madison = get_cd(ptc_table, 0)
    cds_jay = get_cd(ptc_table, 1)
    cds_hamilton = get_cd(ptc_table, 2)

    print(t_star_itc)

    print("Class Hamilton : ", end="")
    print(cds_hamilton)
    print("Class Madison : ", end="")
    print(cds_madison)
    print("Class Jay : ", end="")
    print(cds_jay)


