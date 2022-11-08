import math
import sqlite3
import struct
from collections import OrderedDict
from typing import Tuple
from io import StringIO
import numpy as np
import itertools

from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex, SoundexIndex, DiskIndexWriter
from indexing import DiskPositionalIndex
from indexing.soundexindex import SoundexIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
from text.soundextokenprocessor import SoundexTokenProcessor
import time
from porter2stemmer import Porter2Stemmer
import os
import numpy as np
import json
from pathlib import Path

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus, typ: int, corpus_path: str):
    # Typ 0 - .txt
    # Typ 1 - .json
    token_processor = AdvancedTokenProcessor()
    soundex_processor = SoundexTokenProcessor()
    ind = InvertedIndex()
    soundex = SoundexIndex()
    ld_dict = {}

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        wdt_sum = 0
        this_doc_hash = {}
        for position, s in enumerate(stream):
            processed_token_list = token_processor.process_token(s)
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
        # if type == 0:
        #     for position, s in enumerate(stream):
        #         ind.add_term(token_processor.process_token(s), d.id, position + 1)
        # else:
        #     auth = EnglishTokenStream(d.getAuthor())
        #     for position, s in enumerate(stream):
        #         ind.add_term(token_processor.process_token(s), d.id, position + 1)
        #
        #     for ss in auth:
        #         soundex.add_term(soundex_processor.process_token(ss), d.id)

    diw = DiskIndexWriter()
    diw.writeIndex(ind, corpus_path, ld_dict)


if __name__ == "__main__":
    booleanQueryParser = BooleanQueryParser()

    corpus_path = input("Enter the path for corpus: ")

    # TODO: Take input from user to ask for build or query the index
    print("1. Build Corpus")
    print("2. Query Corpus")
    query_build_inp = input()

    if query_build_inp == '1':
        typ = -1
        if os.listdir(corpus_path)[0].endswith('.json'):
            d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
            typ = 1
        else:
            d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
            typ = 0

        print("Indexing started....")
        start = time.time()
        # Build the index over this directory.
        index_corpus(d, typ, corpus_path)
        elapsed = time.time() - start
        print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                                   time.gmtime(elapsed)))
    elif query_build_inp == '2':
        query = ""
        print("1. Boolean query Mode")
        print("2. Ranked query Mode")
        mode = input()
        disk_positional_index = DiskPositionalIndex(corpus_path)
        token_processor = AdvancedTokenProcessor()
        if os.listdir(corpus_path)[0].endswith('.json'):
            d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
            typ = 1
        else:
            d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
            typ = 0
        d.documents()

        if mode == '1':
            while True:
                pList = []
                query = input("Enter query: ")
                # TODO: Do special Queries - Done
                if query[0] == ":":
                    if query[1:5] == "stem":
                        print(Porter2Stemmer().stem(query[5:]))
                        continue
                    # TODO: Do the same for Soundex
                    # elif query[1:7] == "author":
                    #     postings = soundex_index.getPostings(SoundexTokenProcessor().process_token(query[8:]))
                    #     for p in postings:
                    #         auth = EnglishTokenStream(d.get_document(p.doc_id).getAuthor())
                    #         print(f"Title: {d.get_document(p.doc_id).getTitle}")
                    #         print("Author:", end=" ")
                    #         for ss in auth:
                    #             print(ss, end=" ")
                    #         print()
                    #     print(f"Total documents with author name '{query[8:]}' in it: {len(postings)}")
                    #     continue
                    elif query[1:6] == "index":
                        # TODO - Restart program - Done
                        corpus_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/" + query[7:]

                        if os.listdir(corpus_path)[0].endswith('.json'):
                            d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
                            typ = 1
                        else:
                            d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
                            typ = 0

                        print("Indexing started....")
                        start = time.time()
                        # Build the index over this directory.
                        index_corpus(d, typ, corpus_path)
                        elapsed = time.time() - start
                        print("Finished Indexing. Elapsed time = " + time.strftime(
                            "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                            time.gmtime(elapsed)))
                        continue
                    elif query[1:6] == "vocab":
                        vocab = disk_positional_index.getVocabulary()
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
                postings = booleanQueryParser.parse_query(query).get_postings(disk_positional_index)

                print(f"The query '{query}' is found in documents: ")
                doc_ids = []
                for posting in postings:
                    pList.append(d.get_document(posting.doc_id).getTitle)
                    doc_ids.append(posting.doc_id)

                if len(pList) == 0:
                    print("No documents found")
                    continue
                else:
                    for ele in postings:
                        print(f"{d.get_document(ele.doc_id)}")
                    print(f"Length of Documents: {len(pList)}")

                user_choice = ""
                while True:
                    user_choice = input("Would you like to view any document from the list?(y/n)")
                    if user_choice == 'y' or user_choice == 'Y':
                        doc_choice = input("Please choose the doc_id of the document: ")
                        if doc_choice.isnumeric() and int(doc_choice) in doc_ids:
                            # TODO: print that document
                            cont = EnglishTokenStream(d.get_document(int(doc_choice)).getContent())
                            strCont = []
                            count = 0
                            for ss in cont:
                                if count == 20:
                                    count = 0
                                    print()
                                print(ss, end=" ")
                                count += 1
                        else:
                            print("Not a valid option")
                    elif user_choice == 'n' or user_choice == 'N':
                        break
                    else:
                        print("Not a valid input")
        elif mode == '2':
            # Ranked query mode
            print("1. Default method")
            print("2. tf-idf method")
            print("3. Okapi BM25")
            print("4. Wacky")
            choice = input()
            size_of_corpus = len([entry for entry in os.listdir(corpus_path) if os.path.isfile(os.path.join(corpus_path, entry))]) - 4
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

                    accumulator_dict = OrderedDict(sorted(accumulator_dict.items(),
                                                      key=lambda item: item[1],
                                                      reverse=True))

                    out = dict(itertools.islice(accumulator_dict.items(), 10))
                    for key, value in out.items():
                        print(d.get_document(key).getTitle, end="")
                        print(" - " + str(value))
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
