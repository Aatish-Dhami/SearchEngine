from formulas.variants import Variants
from text.englishtokenstream import EnglishTokenStream
from io import StringIO
import struct
import numpy as np


class WackyVariant(Variants):
    def get_accumulator_dict(self, query, path, dp_index, token_processor):
        mStream = EnglishTokenStream(StringIO(query))
        pathDW = path + "/docWeights.bin"
        pathSC = path + "/sizeOfCorpus.bin"
        dwfile = open(pathDW, "rb")
        socFile = open(pathSC, "rb")
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
                tftd = len(posting.get_positions())
                temp = self._get_wdt(self, tftd) * wqt
                # Get LD

                dwfile.seek(8 * posting.doc_id)
                file_contents = dwfile.read(8)
                ld = struct.unpack("d", file_contents)[0]
                if posting.doc_id in accumulator_dict:
                    # Increment
                    accumulator_dict[posting.doc_id] += (temp / ld)
                else:
                    # Create new
                    accumulator_dict[posting.doc_id] = (temp / ld)

        return accumulator_dict

    def _get_wqt(self, n, dft):
        return np.log(1 + (n/dft))

    def _get_wdt(self, tftd):
        return 1 + np.log(tftd)
