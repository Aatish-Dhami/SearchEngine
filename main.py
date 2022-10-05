from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
import time
from porter2stemmer import Porter2Stemmer
import os
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request, jsonify

import json
from pathlib import Path

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = AdvancedTokenProcessor()
    ind = InvertedIndex()

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        for position, s in enumerate(stream):
            ind.add_term(token_processor.process_token(s), d.id, position + 1)
    return ind


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


@app.route('/for_query', methods=['GET', 'POST'])
def query_search():
    query = request.form['query']
    directory = request.form['directory']

    # text2 = request.form['text2']
    result = getListOfDocuments(query, directory)

    # result = {
    #     "output": combine
    # }
    # result = {str(key): value for key, value in result.items()}
    print(result)
    # jsonify(result=result)
    return result


def getTimeForIndexing(corpus_path):
    # "/Users/zenil/IdeaProjects/CECE529_homework1/MobyDick10Chapters"

    if os.listdir(corpus_path)[0].endswith('.json'):
        getTimeForIndexing.d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    else:
        getTimeForIndexing.d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    start = time.time()
    # Build the index over this directory.
    getTimeForIndexing.index = index_corpus(getTimeForIndexing.d)
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
        elif query[1:6] == "index":
            # TODO - Restart program - Done
            corpus_path = "/Users/zenil/IdeaProjects/SearchEngine/data/" + query[7:]

            if os.listdir(corpus_path)[0].endswith('.json'):
                getTimeForIndexing.d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
            else:
                getTimeForIndexing.d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

            print("Indexing started....")
            start = time.time()
            # Build the index over this directory.
            getTimeForIndexing.index = index_corpus(getTimeForIndexing.d)
            elapsed = time.time() - start

            indextime_for_newdirectory = time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                       time.gmtime(elapsed))
            return [indextime_for_newdirectory]


        elif query[1:6] == "vocab":
            vocab_list = []
            vocab = getTimeForIndexing.index.getVocabulary()

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
            return "Invalid Special Query"
    booleanQueryParser = BooleanQueryParser()
    postings = booleanQueryParser.parse_query(query).get_postings(getTimeForIndexing.index)

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


if __name__ == "__main__":
    app.run(debug=True)
    # booleanQueryParser = BooleanQueryParser()

    # corpus_path = input("Enter the path for corpus: ")
    #
    # if os.listdir(corpus_path)[0].endswith('.json'):
    #     d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    # else:
    #     d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    #
    # print("Indexing started....")
    # start = time.time()
    # # Build the index over this directory.
    # index = index_corpus(d)
    # elapsed = time.time() - start
    # print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
    #                                                            time.gmtime(elapsed)))

    # query = ""
    # while True:
    #     pList = []
    #     query = input("Enter query: ")
    #     # TODO: Do special Queries
    #     if query[0] == ":":
    #         if query[1:5] == "stem":
    #             print(Porter2Stemmer().stem(query[5:]))
    #             continue
    #         elif query[1:6] == "index":
    #             # TODO - Restart program - Done
    #             corpus_path = "/Users/zenil/IdeaProjects/SearchEngine/" + query[7:]
    #
    #             if os.listdir(corpus_path)[0].endswith('.json'):
    #                 d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    #             else:
    #                 d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    #
    #             print("Indexing started....")
    #             start = time.time()
    #             # Build the index over this directory.
    #             index = index_corpus(d)
    #             elapsed = time.time() - start
    #             print("Finished Indexing. Elapsed time = " + time.strftime(
    #                 "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
    #                 time.gmtime(elapsed)))
    #             continue
    #         elif query[1:6] == "vocab":
    #             vocab = index.getVocabulary()
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
    #     # Processing the query as terms
    # postings = booleanQueryParser.parse_query(query).get_postings(index)
    #
    # print(f"The query '{query}' is found in documents: ")
    # for posting in postings:
    #     pList.append(d.get_document(posting.doc_id).getTitle)
    #
    # if len(pList) == 0:
    #     print("No documents found")
    # else:
    #     for sr, ele in enumerate(sorted(pList)):
    #         print(f"{sr + 1}. {ele}")
    #     print(f"Length of Documents: {len(pList)}")

    # user_choice = ""
    # while True:
    #     user_choice = input("Would you like to view any document from the list?(y/n)")
    #     if user_choice == 'y' or user_choice == 'Y':
    #         doc_choice = input("Please choose the serial number of the document: ")
    #         if doc_choice.isnumeric() and 1 <= int(doc_choice) <= len(pList):
    #             # TODO: print that document
    #             document = d.get_document(int(doc_choice) - 1)
    #             print(document)
    #             # with open(corpus_path, 'r') as file:
    #             #     print(json.load(file).get('body'))
    #         else:
    #             print("Not a valid option")
    #     elif user_choice == 'n' or user_choice == 'N':
    #         break
    #     else:
    #         print("Not a valid input")

# test Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/test
# Moby Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/MobyDick10Chapters
# Npss Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/all-nps-sites-extracted
