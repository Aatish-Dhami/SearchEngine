import math

from variants.variants import Variants
from text.englishtokenstream import EnglishTokenStream
from io import StringIO
import struct
import numpy as np


class WackyVariant(Variants):
    def get_accumulator_dict(self, query, path, dp_index, token_processor):
        mStream = EnglishTokenStream(StringIO(query))
        pathDW = path + "/docWeights.bin"
        pathSC = path + "/sizeOfCorpus.bin"
        pathDLA = path + "/docLengthA.bin"
        socFile = open(pathSC, "rb")
        dlaFile = open(pathDLA, "rb")
        dwfile = open(pathDW, "rb")
        accumulator_dict = {}
        size_of_corpus = struct.unpack("i", socFile.read())

        # get docLengthA
        docLengthA = struct.unpack("d", dlaFile.read(8))[0]

        for term in mStream:
            processed_token_list = token_processor.process_token(term)
            tPostingList = dp_index.getPostings(processed_token_list[-1])
            dft = len(tPostingList)

            # calculate wqt
            wqt = self._get_wqt(self, size_of_corpus[0], dft)

            # Calculate score for every document
            for posting in tPostingList:

                # get byteSize & avgTftd
                dwfile.seek((32 * posting.doc_id) + 16)
                byteSize = struct.unpack("d", dwfile.read(8))[0]
                dwfile.seek((32 * posting.doc_id) + 24)
                avgTftd = struct.unpack("d", dwfile.read(8))[0]

                # compute wqt * wdt
                tftd = len(posting.get_positions())
                temp = posting.wdt[3] * wqt

                # Get ld
                ld = self._get_ld(self, byteSize)

                if posting.doc_id in accumulator_dict:
                    # Increment
                    accumulator_dict[posting.doc_id] += (temp / ld)
                else:
                    # Create new
                    accumulator_dict[posting.doc_id] = (temp / ld)

        return accumulator_dict

    def _get_wqt(self, n, dft):
        return max(0, np.log((n-dft)/dft))

    def _get_wdt(self, posting):
        return posting.get_wdt[4]

    def _get_ld(self, byteSize):
        return math.sqrt(byteSize)
