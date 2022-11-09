from .tokenprocessor import TokenProcessor
import re


class SoundexTokenProcessor(TokenProcessor):
    """Algorithms for such phonetic hashing are commonly collectively known as SOUNDEX soundex algorithms.

    The variations in different soundex algorithms have to do with the conversion of
    terms to 4-character forms. A commonly used conversion results in a 4-character code, with the first character
    being a letter of the alphabet and the other three being digits between 0 and 9.
    1. Retain the first letter of the term.
    2. Change all occurrences of the following letters to ’0’ (zero): ’A’, E’, ’I’, ’O’, ’U’, ’H’, ’W’, ’Y’.
    3. Change letters to digits as follows:
        B, F, P, V to 1.
        C, G, J, K, Q, S, X, Z to 2.
        D,T to 3.
        L to 4.
        M, N to 5.
        R to 6.
    4. Repeatedly remove one out of each pair of consecutive identical digits.
    5. Remove all zeros from the resulting string. Pad the resulting string with trailing zeros and return the first
        four positions, which will consist of a letter followed by three digits. """

    def process_token(self, token: str) -> str:
        token = token.upper()
        fhashcode = token[0]
        hashcode = ""
        dictionary = {"AEIOUHWY": ".",
                      "BFPV": "1",
                      "CGJKQSXZ": "2",
                      "DT": "3",
                      "L": "4",
                      "MN": "5",
                      "R": "6"
                      }

        # Encoding
        for char in token[1:]:
            for key in dictionary.keys():
                if char in key:
                    code = dictionary[key]
                    if code != '.':
                        if code != fhashcode[-1]:
                            fhashcode += code

        i = 0
        while i < len(fhashcode) - 1:
            hashcode += fhashcode[i]
            if fhashcode[i] != fhashcode[i + 1]:
                i += 1
            else:
                i += 2
        if i < len(fhashcode):
            hashcode += fhashcode[-1]

        hashcode = hashcode[:4].ljust(4, "0")
        return hashcode
