from typing import Tuple
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex, SoundexIndex
from indexing.soundexindex import SoundexIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
from text.soundextokenprocessor import SoundexTokenProcessor
import time
from porter2stemmer import Porter2Stemmer
import os
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request, jsonify

import json
from pathlib import Path

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus, type: int) -> tuple[InvertedIndex, SoundexIndex]:
    # Type 0 - .txt
    # Type 1 - .json
    token_processor = AdvancedTokenProcessor()
    soundex_processor = SoundexTokenProcessor()
    ind = InvertedIndex()
    soundex = SoundexIndex()

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        if type == 0:
            for position, s in enumerate(stream):
                ind.add_term(token_processor.process_token(s), d.id, position + 1)
        else:
            auth = EnglishTokenStream(d.getAuthor())
            for position, s in enumerate(stream):
                ind.add_term(token_processor.process_token(s), d.id, position + 1)

            for ss in auth:
                soundex.add_term(soundex_processor.process_token(ss), d.id)

    return ind, soundex


# initialise app
app = Flask(__name__, template_folder='templates')  # still relative to module


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/for_path', methods=['GET', 'POST'])
def path_post():
    path = request.form['path']
    time = getTimeForIndexing(path)
    return time

@app.route('/for_doc', methods=['GET', 'POST'])
def path_post():
    docID = request.form['doc_id']
    response = getDocData(docID)
    return response

@app.route('/for_query', methods=['GET', 'POST'])
def query_search():
    query = request.form['query']
    directory = request.form['directory']
    word = request.args.get('text1')
    # text2 = request.form['text2']
    result = getListOfDocuments(query, directory)

    # result = {
    #     "output": combine
    # }
    # result = {str(key): value for key, value in result.items()}
    print(result)
    # jsonify(result=result)
    return result


def getTimeForIndexing(corpus_path1):
    # /Users/zenil/IdeaProjects/CECE529_homework1/MobyDick10Chapters

    getTimeForIndexing.corpus_path = corpus_path1
    type = -1
    if os.listdir(getTimeForIndexing.corpus_path)[0].endswith('.json'):
        getTimeForIndexing.d = DirectoryCorpus.load_json_directory(getTimeForIndexing.corpus_path, ".json")
        type = 1
    else:
        getTimeForIndexing.d = DirectoryCorpus.load_text_directory(getTimeForIndexing.corpus_path, ".txt")
        type = 0

    print("Indexing started....")
    start = time.time()
    # Build the index over this directory.

    getTimeForIndexing.inverted_index, getTimeForIndexing.soundex_index = index_corpus(getTimeForIndexing.d, type)
    elapsed = time.time() - start
    print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                               time.gmtime(elapsed)))
    total_time = time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11], time.gmtime(elapsed))
    return total_time


def getListOfDocuments(query, directory):
    if query[0] == ":":
        if query[1:5] == "stem":
            stemOutput = Porter2Stemmer().stem(query[5:])
            stemList = [stemOutput]
            return stemList
        elif query[1:7] == "author":
            author_list = []
            postings = getTimeForIndexing.soundex_index.getPostings(SoundexTokenProcessor().process_token(query[8:]))

            for p in postings:
                auth = EnglishTokenStream(getTimeForIndexing.d.get_document(p.doc_id).getAuthor())
                print(auth)
                author_list.append("Title:" + getTimeForIndexing.d.get_document(p.doc_id).getTitle)
                print(f"Title: {getTimeForIndexing.d.get_document(p.doc_id).getTitle}")
                author_list.append("Author: ")
                print("Author:", end=" ")
                for ss in auth:
                    print(ss, end=" ")
                    author_list.append(ss)
                print()
            print(f"Total documents with author name '{query[8:]}' in it: {len(postings)}")
            author_list.append("Total documents with author name " + query[8:] + " in it: " + str(len(postings)))
            return author_list
        elif query[1:6] == "index":
            # TODO - Restart program - Done
            corpus_path = "/Users/zenil/IdeaProjects/CECE529_homework1/data/" + query[7:]

            if os.listdir(corpus_path)[0].endswith('.json'):
                getTimeForIndexing.d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
                type = 1
            else:
                getTimeForIndexing.d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
                type = 0

            print("Indexing started....")
            start = time.time()
            # Build the index over this directory.
            getTimeForIndexing.inverted_index, getTimeForIndexing.soundex_index = index_corpus(getTimeForIndexing.d,
                                                                                               type)
            elapsed = time.time() - start

            indextime_for_newdirectory = time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                       time.gmtime(elapsed))
            return [indextime_for_newdirectory]


        elif query[1:6] == "vocab":
            vocab_list = []
            vocab = getTimeForIndexing.inverted_index.getVocabulary()

            if len(vocab) > 1000:
                for i in range(1000):
                    print(vocab[i])
                    vocab_list.append(vocab[i])
            else:
                for i in range(len(vocab)):
                    print(vocab[i])
                    vocab_list.append(vocab[i])
            vocab_list.append("Length of Vocabulary : " + str(len(vocab)))
            print(f"Length of Vocabulary: {len(vocab)}")
            return vocab_list
        elif query[1] == "q":
            return ["q"]
        else:
            print("Invalid special query")
            return ["Invalid Special Query"]
    booleanQueryParser = BooleanQueryParser()
    postings = booleanQueryParser.parse_query(query).get_postings(getTimeForIndexing.inverted_index)

    print(f"The query '{query}' is found in documents: ")
    docResult = []
    pList = []
    for posting in postings:
        pList.append(getTimeForIndexing.d.get_document(posting.doc_id).getTitle)

    if len(pList) == 0:
        print("No documents found")
        return ["No Documents Found"]
    else:
        for sr, ele in enumerate(sorted(pList)):
            print(f"{sr + 1}. {ele}")
            temp_with_serial = str(sr + 1) + "." + ele
            docResult.append(temp_with_serial)
        print(f"Length of Documents: {len(pList)}")
        return docResult

def getDocData(docId):
    # TODO: print that document
    cont = EnglishTokenStream(getTimeForIndexing.d.get_document(int(docId)).getContent())
    strCont = []
    count = 0
    for ss in cont:
        if count == 20:
            count = 0
            print()
        print(ss, end=" ")
        strCont.append(ss)
        count += 1
    return strCont
if __name__ == "__main__":
    app.run(debug=True)
    # booleanQueryParser = BooleanQueryParser()
    #
    # corpus_path = input("Enter the path for corpus: ")
    # type = -1
    # if os.listdir(corpus_path)[0].endswith('.json'):
    #     d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    #     type = 1
    # else:
    #     d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    #     type = 0
    #
    # print("Indexing started....")
    # start = time.time()
    # # Build the index over this directory.
    #
    # inverted_index, soundex_index = index_corpus(d, type)
    # elapsed = time.time() - start
    # print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
    #                                                            time.gmtime(elapsed)))
    #
    # query = ""
    # while True:
    #     pList = []
    #     query = input("Enter query: ")
    #     # TODO: Do special Queries - Done
    #     if query[0] == ":":
    #         if query[1:5] == "stem":
    #             print(Porter2Stemmer().stem(query[5:]))
    #             continue
    #         elif query[1:7] == "author":
    #             postings = soundex_index.getPostings(SoundexTokenProcessor().process_token(query[8:]))
    #             for p in postings:
    #                 auth = EnglishTokenStream(d.get_document(p.doc_id).getAuthor())
    #                 print(f"Title: {d.get_document(p.doc_id).getTitle}")
    #                 print("Author:", end=" ")
    #                 for ss in auth:
    #                     print(ss, end=" ")
    #                 print()
    #             print(f"Total documents with author name '{query[8:]}' in it: {len(postings)}")
    #             continue
    #         elif query[1:6] == "index":
    #             # TODO - Restart program - Done
    #             corpus_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/" + query[7:]
    #
    #             if os.listdir(corpus_path)[0].endswith('.json'):
    #                 d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    #             else:
    #                 d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    #
    #             print("Indexing started....")
    #             start = time.time()
    #             # Build the index over this directory.
    #             inverted_index, soundex_index = index_corpus(d, type)
    #             elapsed = time.time() - start
    #             print("Finished Indexing. Elapsed time = " + time.strftime(
    #                 "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
    #                 time.gmtime(elapsed)))
    #             continue
    #         elif query[1:6] == "vocab":
    #             vocab = inverted_index.getVocabulary()
    #             if len(vocab) > 1000:
    #                 for i in range(1000):
    #                     print(vocab[i])
    #             else:
    #                 for i in range(len(vocab)):
    #                     print(vocab[i])
    #             print(f"Length of Vocabulary: {len(vocab)}")
    #             continue
    #         elif query[1] == "q":
    #             break
    #         else:
    #             print("Invalid special query")
    #             continue
    #
    #     # Processing the query as terms
    #     postings = booleanQueryParser.parse_query(query).get_postings(inverted_index)
    #
    #     print(f"The query '{query}' is found in documents: ")
    #     doc_ids = []
    #     for posting in postings:
    #         pList.append(d.get_document(posting.doc_id).getTitle)
    #         doc_ids.append(posting.doc_id)
    #
    #     if len(pList) == 0:
    #         print("No documents found")
    #         continue
    #     else:
    #         for ele in postings:
    #             print(f"{d.get_document(ele.doc_id)}")
    #         print(f"Length of Documents: {len(pList)}")
    #
    #     user_choice = ""
    #     while True:
    #         user_choice = input("Would you like to view any document from the list?(y/n)")
    #         if user_choice == 'y' or user_choice == 'Y':
    #             doc_choice = input("Please choose the doc_id of the document: ")
    #             if doc_choice.isnumeric() and int(doc_choice) in doc_ids:
    #                 # TODO: print that document
    #                 cont = EnglishTokenStream(d.get_document(int(doc_choice)).getContent())
    #                 strCont = []
    #                 count = 0
    #                 for ss in cont:
    #                     if count == 20:
    #                         count = 0
    #                         print()
    #                     print(ss, end=" ")
    #                     count += 1
    #             else:
    #                 print("Not a valid option")
    #         elif user_choice == 'n' or user_choice == 'N':
    #             break
    #         else:
    #             print("Not a valid input")

# test Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/test
# Moby Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/MobyDick10Chapters
# Npss Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/all-nps-sites-extracted
# tsta PATH: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/testauth
# 4000 Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/mlb-articles-4000
