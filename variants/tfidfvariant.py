from variants.variants import Variants
from text.englishtokenstream import EnglishTokenStream
from io import StringIO
import struct
import numpy as np


class TfidfVariant(Variants):
    def get_accumulator_dict(self, query, path, dp_index, token_processor):
        mStream = EnglishTokenStream(StringIO(query))
        pathDW = path + "/docWeights.bin"
        pathSC = path + "/sizeOfCorpus.bin"
        socFile = open(pathSC, "rb")
        dwfile = open(pathDW, "rb")
        accumulator_dict = {}
        size_of_corpus = struct.unpack("i", socFile.read())

        for term in mStream:
            processed_token_list = token_processor.process_token(term)
            tPostingList = dp_index.getPostings(processed_token_list[-1])
            dft = len(tPostingList)

            # calculate wqt
            wqt = self._get_wqt(self, size_of_corpus[0], dft)

            # Calculate score for every document
            for posting in tPostingList:

                # compute wqt * wdt
                # tftd = len(posting.get_positions())
                temp = posting.wdt[1] * wqt

                # Get docWeights
                dwfile.seek(32 * posting.doc_id)
                file_contents = dwfile.read(8)
                docWeights = struct.unpack("d", file_contents)[0]

                ld = self._get_ld(self, docWeights)

                if posting.doc_id in accumulator_dict:
                    # Increment
                    accumulator_dict[posting.doc_id] += (temp / ld)
                else:
                    # Create new
                    accumulator_dict[posting.doc_id] = (temp / ld)

        return accumulator_dict

    def _get_wqt(self, n, dft):
        return np.log(n/dft)

    def _get_wdt(self, posting):
        return posting.get_wdt[1]

    def _get_ld(self, docW):
        return docW