import os
from unidecode import unidecode
import string


def get_nbib_files(folder=None):
    directory = os.curdir
    if folder is not None:
        directory = folder
    the_files = []
    for file in os.listdir(directory):
        if file.endswith(".nbib"):
            the_files.append("/".join([directory, file]))
    return the_files


def generate_key(the_current_keys, the_record):
    if the_record["author"]:
        the_key = str(the_record["author"][0]).split(sep=", ")[0]
    else:
        the_key = the_record["title"][0:5]
    the_key += the_record["year"]
    the_key = the_key.replace(" ", "")
    the_key = unidecode(the_key).replace("'", "").replace("?", "")

    index = -1
    while the_key in the_current_keys:
        index += 1
        the_key = the_key + string.ascii_letters[index]

    return the_key


def record_builder():
    return {
        'author': [],
        'year': None,
        'title': None,
        'journal': None,
        'volume': None,
        'number': None,
        'doi': None,
        'keywords': [],
        'abstract': None,
        'pages': None
    }


def parse_line(the_record, the_line):
    if the_line.startswith("TI"):
        the_record["title"] = the_line.replace("TI  - ", "").replace("\n", "")
    elif the_line.startswith("AU"):
        the_record["author"].append(the_line.replace("AU  - ", "").replace("\n", ""))
    elif the_line.startswith("DP"):
        the_record["year"] = the_line.replace("DP  - ", "").replace("\n", "")[-4:]
    elif the_line.startswith("JT"):
        the_record["journal"] = the_line.replace("JT  - ", "").replace("\n", "")
    elif the_line.startswith("VI"):
        the_record["volume"] = the_line.replace("VI  - ", "").replace("\n", "")
    elif the_line.startswith("IP"):
        the_record["number"] = the_line.replace("IP  - ", "").replace("\n", "")
    elif the_line.startswith("PG"):
        the_record["pages"] = the_line.replace("PG  - ", "").replace("\n", "")
    elif the_line.startswith("AB"):
        the_record["abstract"] = the_line.replace("AB  - ", "").replace("\n", "").replace("%", "\\%")
    elif the_line.startswith("AID"):
        the_record["doi"] = the_line.replace("AID - ", "").replace("\n", "")
    elif the_line.startswith("OT"):
        the_record["keywords"].append(the_line.replace("OT  - ", "").replace("\n", ""))


def parse_to_bib(the_record, the_key):
    the_lines = ["@article{" + the_key]
    for k, v in the_record.items():
        if v is None:
            continue
        if type(v) == list:
            if k == "author":
                bib_line = k + " = {" + " and ".join(v) + "}"
            elif k == "keywords":
                bib_line = k + " = {" + "; ".join(v) + "}"
        else:
            bib_line = k + " = {" + v + "}"

        the_lines.append(bib_line)

    result = ", \n".join(the_lines)

    return result + "\n}\n\n"


if __name__ == '__main__':

    nbib_files = get_nbib_files("new_nbib")

    record_list = []
    for n_file in nbib_files:
        with open(n_file, mode="r") as nbib_file:
            for line in nbib_file:
                if line == "\n" or line.strip() == "":
                    continue
                if line.startswith("OWN"):
                    record_list.append(record_builder())
                    continue

                last_record = record_list[-1]
                parse_line(last_record, line)

    current_keys = []
    with open("output_bib/related.bib", "w") as bib_file:
        for record in record_list:
            record_key = generate_key(current_keys, record)
            current_keys.append(record_key)
            bib_record = parse_to_bib(record, the_key=record_key)
            bib_file.write(bib_record)
