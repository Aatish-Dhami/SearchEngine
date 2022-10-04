def soundex_generator(token):

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

# driver code
print(soundex_generator('Hera'))