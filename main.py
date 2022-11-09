import math
import struct
from io import StringIO
from documents import DocumentCorpus, DirectoryCorpus
from indexing import InvertedIndex, SoundexIndex, DiskIndexWriter
from indexing import DiskPositionalIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
from text.soundextokenprocessor import SoundexTokenProcessor
import time
from porter2stemmer import Porter2Stemmer
import os
import numpy as np
import heapq as hq

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus, typ: int, corpus_path: str):
    # Typ 0 - .txt
    # Typ 1 - .json
    print("Indexing started....")
    start = time.time()
    tkn_processor = AdvancedTokenProcessor()
    soundex_processor = SoundexTokenProcessor()
    ind = InvertedIndex()
    soundex = SoundexIndex()
    diw = DiskIndexWriter()
    ld_dict = {}

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        wdt_sum = 0
        this_doc_hash = {}
        for position, s in enumerate(stream):
            processed_token_list = tkn_processor.process_token(s)
            ind.add_term(processed_token_list, d.id, position + 1)

            # calculating tftd
            if processed_token_list[-1] in this_doc_hash.keys():
                this_doc_hash[processed_token_list[-1]] += 1
            else:
                this_doc_hash[processed_token_list[-1]] = 1

        # Calculate (wdt)^2 sum
        for key, value in this_doc_hash.items():
            # Get wdt for every term from tftd using this_doc_hash
            wdt = 1 + np.log(value)
            wdt_sum += wdt * wdt

        # Calculate ld and insert into ld dict for this document
        ld_dict[d.id] = math.sqrt(wdt_sum)

        # getting authors for soundex
        if typ == 1:
            auth = EnglishTokenStream(d.getAuthor())
            for ss in auth:
                soundex.add_term(soundex_processor.process_token(ss), d.id)

    diw.writeIndex(ind, corpus_path, ld_dict)
    diw.writeSoundexIndex(soundex, corpus_path)
    elapsed = time.time() - start
    print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                               time.gmtime(elapsed)))


def boolean_mode(dpIndex, dd, path):
    while True:
        pList = []
        query = input("Enter query: ")
        if query[0] == ":":
            if query[1:5] == "stem":
                print(Porter2Stemmer().stem(query[5:]))
                continue
            elif query[1:7] == "author":
                postings = dpIndex.getPostingsSoundex(SoundexTokenProcessor().process_token(query[8:]))
                for p in postings:
                    auth = EnglishTokenStream(dd.get_document(p.doc_id).getAuthor())
                    print(f"Title: {dd.get_document(p.doc_id).getTitle}")
                    print("Author:", end=" ")
                    for ss in auth:
                        print(ss, end=" ")
                    print()
                print(f"Total documents with author name '{query[8:]}' in it: {len(postings)}")
                continue
            elif query[1:6] == "index":
                path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/" + query[7:]
                dd, f_type = load_directory(path)
                # Build the index over this directory.
                index_corpus(dd, f_type, path)
                continue
            elif query[1:6] == "vocab":
                vocab = dpIndex.getVocabulary()
                if len(vocab) > 1000:
                    for i in range(1000):
                        print(vocab[i])
                else:
                    for i in range(len(vocab)):
                        print(vocab[i])
                print(f"Length of Vocabulary: {len(vocab)}")
                continue
            elif query[1] == "q":
                break
            else:
                print("Invalid special query")
                continue

        # Processing the query as terms
        postings = booleanQueryParser.parse_query(query).get_postings(dpIndex)

        print(f"The query '{query}' is found in documents: ")
        doc_ids = []
        for posting in postings:
            print(d.get_document(posting.get_document_id()).getTitle, end="")
            print(" (DOCID " + str(posting.get_document_id()) + ")")
            doc_ids.append(posting.get_document_id())
        print(f"Length of Documents: {len(postings)}")

        while True:
            user_choice = input("Would you like to view any document from the list?(y/n)")
            if user_choice == 'y' or user_choice == 'Y':
                doc_choice = input("Please choose the doc_id of the document: ")

                if doc_choice.isnumeric() and int(doc_choice) in doc_ids:
                    printDocument(doc_choice, dd)
                    print()
                else:
                    print("Not a valid option")
            elif user_choice == 'n' or user_choice == 'N':
                break
            else:
                print("Not a valid input")


def printDocument(doc_id, dd):
    cont = EnglishTokenStream(dd.get_document(int(doc_id)).getContent())
    count = 0
    for ss in cont:
        if count == 20:
            count = 0
            print()
        print(ss, end=" ")
        count += 1


def load_directory(path):
    if os.listdir(path)[0].endswith('.json'):
        dd = DirectoryCorpus.load_json_directory(path, ".json")
        fTyp = 1
    else:
        dd = DirectoryCorpus.load_text_directory(path, ".txt")
        fTyp = 0
    return dd, fTyp


if __name__ == "__main__":
    corpus_path = input("Enter the path for corpus: ")
    booleanQueryParser = BooleanQueryParser()
    token_processor = AdvancedTokenProcessor()
    d, fType = load_directory(corpus_path)

    print("1. Build Corpus")
    print("2. Query Corpus")
    query_build_inp = input()

    if query_build_inp == '1':
        # Build the index over this directory.
        index_corpus(d, fType, corpus_path)

    elif query_build_inp == '2':
        disk_positional_index = DiskPositionalIndex(corpus_path)
        query = ""
        print("1. Boolean query Mode")
        print("2. Ranked query Mode")
        mode = input()
        d.documents()

        if mode == '1':
            # TODO: call boolean
            boolean_mode(disk_positional_index, d, corpus_path)
        elif mode == '2':
            # Ranked query mode
            print("1. Default method")
            print("2. tf-idf method")
            print("3. Okapi BM25")
            print("4. Wacky")
            choice = input()
            size_of_corpus = len(
                [entry for entry in os.listdir(corpus_path) if os.path.isfile(os.path.join(corpus_path, entry))]) - 4
            if choice == '1':
                while True:
                    query = input("Enter query: ")
                    if query == ":q":
                        break
                    mStream = EnglishTokenStream(StringIO(query))
                    pathDW = corpus_path + "/docWeights.bin"
                    accumulator_dict = {}

                    for term in mStream:
                        processed_token_list = token_processor.process_token(term)
                        # calculate wqt
                        wqt = disk_positional_index.getWqt(processed_token_list[-1], size_of_corpus)
                        # for every doc in term calculate wdt x wqt
                        tPostingList = disk_positional_index.getPostings(processed_token_list[-1])
                        for posting in tPostingList:
                            # compute wqt * wdt
                            temp = posting.get_wdt() * wqt
                            # Get LD
                            file = open(pathDW, "rb")
                            file.seek(8 * posting.doc_id)
                            file_contents = file.read(8)
                            ld = struct.unpack("d", file_contents)
                            if posting.doc_id in accumulator_dict:
                                # Increment
                                accumulator_dict[posting.doc_id] += (temp / ld)
                            else:
                                # Create new
                                accumulator_dict[posting.doc_id] = (temp / ld)

                    heap = [(-value, key) for key, value in accumulator_dict.items()]
                    largest = hq.nsmallest(10, heap)
                    largest = [(key, -value) for value, key in largest]
                    for tup in largest:
                        print(d.get_document(int(tup[0])).getTitle, end="")
                        print(" - " + str(tup[1][0]))

            elif choice == '2':
                print("This method is work in progress. Coming Soon")
            elif choice == '3':
                print("This method is work in progress. Coming Soon")
            elif choice == '4':
                print("This method is work in progress. Coming Soon")
            else:
                print("Invalid Input")
        else:
            print("Invalid Input")
    else:
        print("Invalid Input")

# test Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/test
# Moby Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/MobyDick10Chapters
# Npss Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/all-nps-sites-extracted
# tsta PATH: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/testauth
# 4000 Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/mlb-articles-4000
