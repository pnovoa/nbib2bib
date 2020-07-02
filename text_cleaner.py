import unidecode as uni
import os
import bibtexparser as bib_par
from cleantext import clean


def get_files_by_extension(folder="bib_files", extension=".bib"):
    the_files = []
    for file in os.listdir(folder):
        if file.endswith(extension):
            the_files.append("/".join([folder, file]))
    return the_files


def process_bib_entry_to_csv_entry(the_entry, the_fields, the_separator):
    result = []
    for field in the_fields:
        if field in the_entry.keys():
            result.append(the_entry[field])
        else:
            result.append("-1")
    return the_separator.join(result)


def clean_str(field_val):
    field_val = field_val.replace("{", "", 1)
    field_val = field_val.replace("}", "", 1)
    field_val = field_val.replace("\t", "")
    field_val = field_val.replace("\n", "")
    field_val = uni.unidecode(field_val)
    return field_val


def parse_to_bib_entry(the_entry, the_fields, the_id):
    result = ["@article{" + the_id]
    for field in the_fields:
        field_val = ''
        if field in the_entry.keys():
            field_val = clean_str(the_entry[field])
        result.append(field + ' = {' + field_val + '}')

    result.append("}")

    return ', \n'.join(result)


# def export_from_bib_to_csv(csv_file="output.csv", list_bib_files=None, fields=None):
#     with open(csv_file, mode='w') as the_csv_file:
#         the_csv_file.writelines(separator.join(fields) + '\n')
#         for bib_file in list_bib_files:
#             with open(bib_file, mode='r') as the_bib_file:
#                 entries = bib_par.load(the_bib_file).entries
#                 for entry in entries:
#                     clean_title = clean(entry['title'], all=True)
#                     abstract_size = len(entry['abstract'])
#                     duplicate_list_value = duplicate_list[clean_title]
#                     if abstract_size == duplicate_list_value and clean_title not in already_added:
#                         the_csv_file.writelines(process_bib_entry_to_csv_entry(entry, fields, separator) + '\n')
#                         already_added.append(clean_title)


if __name__ == '__main__':

    # nltk.download('stopwords')

    # content = []

    # file_names = get_bib_files()
    #
    # for file_name in file_names:
    #     with open(file_name, mode='r') as the_file:
    #         for line in the_file:
    #             if "Early Access Date" in line:
    #                 continue
    #             if line != "":
    #                 _line = line
    #                 if "=" in _line:
    #                     _line = _line.replace(_line[0], _line[0].lower(), 1)
    #
    #                 _line = _line.replace("{{", "{", 1)
    #                 _line = _line.replace("}}", "}", 1)
    #                 _line = _line.replace("\t", "")
    #                 _line = _line.strip()
    #                 _line = uni.unidecode(_line)
    #
    #                 content.append(_line)
    #
    #             else:
    #                 content.append(line)

    FOLDER_BIB = "output_bib"
    OUTPUT_CSV = "related.csv"
    OUTPUT_BIB = "related.bib"
    output_path_bib = "/".join([FOLDER_BIB, OUTPUT_BIB])

    duplicate_list = {}

    final_bib_entries = []
    file_names = get_files_by_extension(FOLDER_BIB)
    ID = 1
    for file_name in file_names:
        with open(file_name, mode='r') as the_bib_file:
            bib_db_entries = bib_par.load(the_bib_file).entries
            for entry in bib_db_entries:
                entry['ID'] = "dce_" + str(ID)
                ID += 1
            final_bib_entries.extend(bib_db_entries)

    separator = "\t"
    fields = ['author', 'year', 'journal', 'volume', 'number', 'pages', 'title', 'abstract']

    with open(output_path_bib, mode='w') as fina_db:
        for entry in final_bib_entries:
            formatted_entry = parse_to_bib_entry(entry, fields, entry['ID'])
            fina_db.writelines(formatted_entry + '\n\n')
            clean_title = clean(clean_str(entry['title']), all=True)
            new_size = 0
            if 'abstract' in entry.keys():
                new_size = len(clean_str(entry['abstract']))
            if clean_title in duplicate_list.keys() and new_size < duplicate_list[clean_title]:
                continue
            duplicate_list[clean_title] = new_size

    # bib_files_list = get_files_by_extension(FOLDER_BIB)
    #
    # for bib_file in bib_files_list:
    #     with open(bib_file, mode='r') as fina_db:
    #         bib_entries = bib_par.load(fina_db).entries
    #         for entry in bib_entries:
    #             clean_title = clean(clean_str(entry['title']), all=True)
    #             new_size = 0
    #             if 'abstract' in entry.keys():
    #                 new_size = len(clean_str(entry['abstract']))
    #             if clean_title in duplicate_list.keys() and new_size < duplicate_list[clean_title]:
    #                 continue
    #             duplicate_list[clean_title] = new_size

    already_added = []
    separator = "\t"
    fields = ['ID', 'author', 'year', 'journal', 'title', 'abstract']

    with open(OUTPUT_CSV, mode='w') as final_csv_file:
        final_csv_file.writelines(separator.join(fields) + '\n')
        bib_files_list = [output_path_bib]
        for bib_file in bib_files_list:
            with open(bib_file, mode='r') as final_file:
                entries = bib_par.load(final_file).entries
                for entry in entries:
                    clean_title = clean(entry['title'], all=True)
                    if clean_title in duplicate_list.keys():
                        duplicate_list_value = duplicate_list[clean_title]
                        abstract_size = 0
                        if 'abstract' in entry.keys():
                            abstract_size = len(entry['abstract'])
                        if abstract_size != duplicate_list_value or clean_title in already_added:
                            continue
                    final_csv_file.writelines(process_bib_entry_to_csv_entry(entry, fields, separator) + '\n')
                    already_added.append(clean_title)
