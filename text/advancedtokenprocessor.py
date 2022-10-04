from porter2stemmer import Porter2Stemmer
from .tokenprocessor import TokenProcessor
import re


class AdvancedTokenProcessor(TokenProcessor):
    """A AdvancedTokenProcessor creates terms from tokens using following rules
    1. Removing all non-alphanumeric characters from the token from end and start.
    2. Converting it to all lowercase.
    3. Remove all apostropes or quotation marks (single or double quotes) from anywhere in the string.
    4. For hyphens in words:
        (a) Removes the hyphens from the token and then proceeds with the modified token;
        (b) Splits the original hyphenated token into multiple tokens without a hyphen, and proceed with all
        split tokens.
    5. Stems the token using an implementation of the Porter2 stemmer."""


    remove_non_alphnum = re.compile(r"^[\W_]+|[\W_]+$")
    double_quotes = '"'
    single_quote = "'"

    def process_token(self, token: str) -> list[str]:
        stemmer = Porter2Stemmer()
        processed_list = []

        processed_token = re.sub(self.remove_non_alphnum, "", token).lower().replace(self.double_quotes, '') \
            .replace(self.single_quote, '')

        if '-' in token:
            processed_list = processed_token.split('-')
            for i in range(len(processed_list)):
                processed_list[i] = stemmer.stem(processed_list[i])
            processed_list.append(processed_token.replace("-", ''))
            return processed_list
        else:
            processed_list.append(stemmer.stem(processed_token))
            return processed_list