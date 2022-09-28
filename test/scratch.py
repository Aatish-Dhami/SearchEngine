import re
from porter2stemmer import Porter2Stemmer

remove_non_alphnum = re.compile(r"^[\W_]+|[\W_]+$")

def process_token(token: str):
    stemmer = Porter2Stemmer()
    double_quotes = '"'
    single_quote = "'"

    processed_token = re.sub(remove_non_alphnum, "", token).lower().replace(double_quotes, '') \
        .replace(single_quote, '')
    processed_list = []
    if '-' in token:
        processed_list = processed_token.split('-')
        for i in range(len(processed_list)):
            processed_list[i] = stemmer.stem(processed_list[i])
        processed_list.append(processed_token.replace("-", ''))
        return processed_list
    else:
        processed_list.append(stemmer.stem(processed_token))
        return processed_list

print(process_token('''H"el'lo.'''))