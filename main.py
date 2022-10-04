from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
import time
from porter2stemmer import Porter2Stemmer
import os
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


if __name__ == "__main__":
    booleanQueryParser = BooleanQueryParser()

    corpus_path = input("Enter the path for corpus: ")

    if os.listdir(corpus_path)[0].endswith('.json'):
        d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    else:
        d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    print("Indexing started....")
    start = time.time()
    # Build the index over this directory.
    index = index_corpus(d)
    elapsed = time.time() - start
    print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                               time.gmtime(elapsed)))

    query = ""
    while True:
        pList = []
        query = input("Enter query: ")
        # TODO: Do special Queries
        if query[0] == ":":
            if query[1:5] == "stem":
                print(Porter2Stemmer().stem(query[5:]))
                continue
            elif query[1:6] == "index":
                # TODO - Restart program
                corpus_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/" + query[7:]

                if os.listdir(corpus_path)[0].endswith('.json'):
                    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
                else:
                    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

                print("Indexing started....")
                start = time.time()
                # Build the index over this directory.
                index = index_corpus(d)
                elapsed = time.time() - start
                print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11],
                                                                           time.gmtime(elapsed)))
                continue
            elif query[1:6] == "vocab":
                vocab = index.getVocabulary()
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
        # Processing the query as terms
        postings = booleanQueryParser.parse_query(query).get_postings(index)

        print(f"The query '{query}' is found in documents: ")
        for posting in postings:
            pList.append(d.get_document(posting.doc_id).getTitle)

        if len(pList) == 0:
            print("No documents found")
        else:
            for sr, ele in enumerate(sorted(pList)):
                print(f"{sr + 1}. {ele}")
            print(f"Length of Documents: {len(pList)}")

        user_choice = ""
        while True:
            user_choice = input("Would you like to view any document from the list?(y/n)")
            if user_choice == 'y' or user_choice == 'Y':
                doc_choice = input("Please choose the serial number of the document: ")
                if doc_choice.isnumeric() and 1 <= int(doc_choice) <= len(pList):
                    #TODO: print that document
                    document = d.get_document(int(doc_choice) - 1)
                    print(document)
                    # with open(corpus_path, 'r') as file:
                    #     print(json.load(file).get('body'))
                else:
                    print("Not a valid option")
            elif user_choice == 'n' or user_choice == 'N':
                break
            else:
                print("Not a valid input")


# test Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/test
# Moby Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/MobyDick10Chapters
# Npss Path: /Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/all-nps-sites-extracted
