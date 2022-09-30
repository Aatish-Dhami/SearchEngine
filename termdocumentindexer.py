from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, TermDocumentIndex , InvertedIndex
from text import BasicTokenProcessor, EnglishTokenStream

"""This basic program builds an InvertedIndex over the .JSON files in 
the folder "all-nps-sites-extracted" of same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    ind = InvertedIndex()

    for d in corpus:
        stream = EnglishTokenStream(d.getContent())
        for position, s in enumerate(stream):
            ind.add_term(token_processor.process_token(s), d.id, position+1)
    return ind


if __name__ == "__main__":
    token_processor = BasicTokenProcessor()
    corpus_path = "/Users/aatishdhami/IdeaProjects/CECS529Python/SearchEngine/Data/all-nps-sites-extracted"
    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    index = index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    query = ""
    while True:
        pList = []
        query = input("Enter a single word query: ")
        if query == "quit":
            break

        # Processing the query as terms
        query = token_processor.process_token(query)
        print(f"The query '{query}' is found in documents: ")
        for p in index.getPostings(query):
            pList.append(d.get_document(p.doc_id).getTitle)

        if len(pList) == 0:
            print("No documents found")
        else:
            print(sorted(pList))
