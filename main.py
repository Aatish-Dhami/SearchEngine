from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex
from queries import BooleanQueryParser
from text import EnglishTokenStream
from text.advancedtokenprocessor import AdvancedTokenProcessor
import time

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = AdvancedTokenProcessor()
    ind = InvertedIndex()

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        for position, s in enumerate(stream):
            ind.add_term(token_processor.process_token(s), d.id, position+1)
    return ind


if __name__ == "__main__":
    booleanQueryParser = BooleanQueryParser()

    corpus_path = input("Enter the path for corpus: ")
    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    # d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    print("Indexing started....")
    start = time.time()
    # Build the index over this directory.
    index = index_corpus(d)
    elapsed = time.time() - start
    print("Finished Indexing. Elapsed time = " + time.strftime("%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:11], time.gmtime(elapsed)))

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    query = ""
    while True:
        pList = []
        query = input("Enter query: ")
        # TODO: Do special Queries
        if query == "quit":
            break

        # Processing the query as terms
        postings = booleanQueryParser.parse_query(query).get_postings(index)

        print(f"The query '{query}' is found in documents: ")
        for posting in postings:
            pList.append(d.get_document(posting.doc_id).getTitle)

        if len(pList) == 0:
            print("No documents found")
        else:
            for sr, ele in enumerate(sorted(pList)):
                print(f"{sr+1}. {ele}")
            print(f"Length of Documents: {len(pList)}")

        user_choice = ""
        while user_choice != 'n' or user_choice != 'N':
            user_choice = input("Would you like to view any document from the list?(y/n)")
            if user_choice == 'y' or user_choice == 'Y':
                doc_choice = input("Please choose the serial number of the document: ")
                if doc_choice.isnumeric() and 1 <= int(doc_choice) + 1 <= len(pList):
                    # print that document
                    print(EnglishTokenStream(d.get_document(int(doc_choice)-1).getContent()))
                else:
                    print("Not a valid option")
            else:
                print("Not a valid input")
