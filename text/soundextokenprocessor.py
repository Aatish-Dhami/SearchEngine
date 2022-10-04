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


    def process_token(self, token: str) -> list[str]:
        pass