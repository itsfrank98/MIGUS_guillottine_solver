import os
from src.utils import write_list_to_file, save_to_pickle, detect_invalid_chars


def clean_paisa_corpus(src, dst):
    """
    Function that cleans the paisa corpus by removing unnecessary fields and leaving only rows with the following fields:
        - token
        - token's lemma
        - token's POS tag
    Also tags denoting the beginning and the end of a document are left. The tags are in the form <text id='..'></text>
    :param src: Path to the directory containing the original corpus
    :param dst: Path to the directory where the cleaned corpus will be saved
    """
    for file in sorted(os.listdir(os.path.join(src))):
        a = []
        delete_line = False
        print(file)
        with open(os.path.join(src, file), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split()
                if delete_line and len(line) > 0 and (line[0] == "1" or line[0] == "<text" or line[0] == "</text>"):
                    delete_line = False
                if len(line) == 0 or (line[0] == "1" and line[1] == "Warning") or line[0] == "#" or line[0] == "##":
                    delete_line = True
                if not delete_line:
                    if line[0] == "<text":  # Add the tag that indicates the beginning of a new text, and the text ID
                        l = line[0] + " " + line[1] + ">"
                    elif line[0] == "</text>":  # Add the tag that indicates the end of the text
                        l = line[0]
                    elif len(line) >= 4:    # Add the line containing word, lemma, POS tag
                        l = line[1] + " " + line[2] + " " + line[4]
                    a.append(l)
        f.close()
        write_list_to_file(a, dst, file)


def build_mwe_dictionaries(dir):
    """
    Function that scans the corpus and builds a dictionary where the keys are the multi-word expressions found, and the values are the number of occurrences of each MWE.
    The dictionary will be later used to build the matrix.
    The criterion according to which a MWE is generated is if it fits some predefined paths. Some additional rules have been considered, since some MWE would result useless
    given the goal of the project.
    :param dir: Directory containing the corpus to analyze
    :return: The computed dictionary
    """
    candidate_mwe_start_tags = ["S", "A", "V"]  # Tags that can denote the beginning of a MWE. The expressions can start with noun, adjective, verb
    candidate_mwe_end_tags = ["A", "B", "NO", "S", "SP", "V"]  # The words that can end a MWE are adjectives, negations, adverbs, nouns, proper nouns, verbs
    auxiliary_verbs = ["essere", "avere"]
    lines_to_skip = ["<text", "</text>"]
    d = dict()
    window = 0  # Variable that keeps track of how many steps we have done since finding the head of the mwe
    mwe_head_tag = ""
    mwe_head_word = ""
    max_window = 3
    for file in sorted(os.listdir(dir)):
        print(file)
        with open(os.path.join(dir, file), "r") as f:
            for line in f:
                line = line.split()
                if line and line[0] not in lines_to_skip:
                    word = line[0].lower()
                    word_tag = line[2]
                    if word_tag in ["FB", "FC", "FS", "FF"]:  # If we meet a punctuation sign, the mwe is broken
                        mwe_head_tag = ""
                        window = 0
                    else:
                        if word.isalpha() and word_tag != "SW" and not detect_invalid_chars(word):
                            window += 1     # Increment the window regardless of the word. If it's not the head of a mwe, it will later be set to 0
                            if window > max_window:     # If the word is too far from the head of the mwe, reset the mwe
                                mwe_head_tag = ""
                                window = 0
                            if not (line[1].lower() in auxiliary_verbs and word_tag == "V"):  # In the corpus, occurrences of the "essere" and "avere" verbs with their declinations, which are auxiliary verbs, are tagged as normal verbs. This would lead to creating unnecessary dictionary keys. Hence, we have to manually recognize these verbs and skip to the next iteration
                                if word_tag in candidate_mwe_start_tags:
                                    if not mwe_head_tag:
                                        mwe_head_tag = word_tag
                                        mwe_head_word = word
                                    else:  # If we already have a candidate mwe
                                        if word_tag in candidate_mwe_end_tags:
                                            if not (mwe_head_tag == "A" and word_tag == "A") and mwe_head_word != word:  # We can't have a MWE made by two adjectives, so we scrap the first and keep the second as beginning of the next MWE. We also are not interested in keys made by two equal words, although with different POS tags
                                                key = mwe_head_word+"_"+word
                                                key2 = word+"_"+mwe_head_word   # If there already exists a key made by the same words but in inverted order, we increment that key's value instead of adding a new one
                                                if key in d.keys():
                                                    d[key] += 1
                                                elif key2 in d.keys():
                                                    d[key2] += 1
                                                else:
                                                    d[key] = 1
                                            if word_tag in candidate_mwe_start_tags:  # The tail of the MWE might be the head of a new MWE, so we add this check
                                                mwe_head_tag = word_tag
                                                mwe_head_word = word
                                        else:
                                            mwe_head_tag = word_tag
                                            mwe_head_word = word
                                    window = 0
                        else:
                            mwe_head_tag = ""
                            window = 0
        f.close()
    return d


if __name__ == '__main__':
    # src = "../paisa_original"
    dir = "../paisa_cleaned1"
    # clean_corpus(src, dir)
    d = build_mwe_dictionaries(dir)
    print(len(d.keys()))
    save_to_pickle(d, "../paisa_dict_numbers.pkl")

