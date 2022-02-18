import bz2
import os
import pickle
import re


def uncompress_to_location(source, dst):
    """
    Uncompress the files into the source directory into json files that are saved in the dst directory
    :param source: Path to the directory containing the bz2 files to uncompress
    :param dst: Path to the directory where the uncompressed files will be serialized
    """
    if not os.path.isdir(os.path.join(dst)):
        os.mkdir(os.path.join(dst))
    for f in sorted(os.listdir(source)):
        zipped = bz2.BZ2File(os.path.join(source, f))
        data = zipped.read()
        open(os.path.join(dst, f.split('.')[0]+".json"), 'wb').write(data)


def write_list_to_file(l, dst, fn):
    if not os.path.isdir(os.path.join(dst)):
        os.mkdir(os.path.join(dst))
    with open(dst+"/"+fn, 'w', encoding='utf-8') as f:
        for row in l:
            f.write(row)
            f.write("\n")
    f.close()


def save_to_pickle(content, fname):
    fp = open(fname, 'wb')
    pickle.dump(content, fp)


def load_from_pickle(fname) -> dict():
    with open(fname, 'rb') as f:
        content = pickle.load(f)
    return content


def write_wiki_list_to_file(l, id, title, dst, fn):
    # Write to file a list of tuples extracted from the wiki corpus. We need a different function because here we take also the id and title parameters
    if not os.path.isdir(os.path.join(dst)):
        os.mkdir(os.path.join(dst))
    with open(dst+"/"+fn, 'w', encoding='utf-8') as f:
        f.write("<text id = \"" + id + "\" title=\"" + title + "\">\n")
        for row in l:
            f.write(row)
            f.write("\n")
        f.write("</text>\n")
    f.close()


def detect_invalid_chars(text):
    # Detect if a string contains characters not used in italian strings
    if re.search("[^\u0061-\u007a\u00e0-\u00e1\u00e8-\u00e9\u00ec\u00ed\u00f2-\u00f3\u00f9\u00fa]", text):
        return True
    else:
        return False


def take_only_dict_relevant_keys(d, d_oc, c1, c2, c3, c4, c5):
    """
    Python's dictionaries use more memory space than the space they occupy on disk. Since it doesn't fit my memory at runtime (i can load it but there's not enough
    space for the other things I need to load) I created this function that takes only the useful entries of the dictionary given the clues and returns them in a new
    dictionary.
    :param d: Original dictionary
    :param d_oc: Occurrences dictionary. This dictionary contains as key only the words having a number of occurrences greater than a certain threshold.
    The original dictionary (d), however, contains pairs of words which include also the words with a low number of occurrences in the corpus. I decided not to remove
    those keys from the dictionary because it required too much time. Therefore, by adding this parameter we allow this function to look only for keys who contain the
    clues and also contain words with a certain number of occurrences.
    :param c1: Clue 1
    :param c2: Clue 2
    :param c3: Clue 3
    :param c4: Clue 4
    :param c5: Clue 5
    :return:
    """
    new_d = dict()
    for k in d.keys():
        if k.startswith(c1+"_") or k.startswith(c2+"_") or k.startswith(c3+"_") or k.startswith(c4+"_") or k.startswith(c5+"_") or \
            k.endswith("_"+c1) or k.endswith("_"+c2) or k.endswith("_"+c3) or k.endswith("_"+c4) or k.endswith("_"+c5):
            if k.split('_')[0] in d_oc.keys() and k.split('_')[1] in d_oc.keys():
                new_d[k] = d[k]
    return new_d


if __name__ == '__main__':
    uncompress_to_location("../w100", "../wiki_json100_uncompressed")
