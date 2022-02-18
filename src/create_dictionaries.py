# File where the dictionaries are created. Spostare qui la creazione dei dizionari paisa e wiki, e da un'altra parte la costruzione della soluzione
import os
from src.utils import load_from_pickle, save_to_pickle
import argparse


def merge_dicts(path_to_d1, path_to_d2, merged_dict_name):
    """
    Loads two dictionaries and merges the second into the first. It then saves the result. I decided to load the dicts
    inside the function instead of passing them as parameters to avoid memory issues.
    :param path_to_d1: Path to the first dictionary
    :param path_to_d2: Path to the second dictionary
    """
    d1 = load_from_pickle(path_to_d1)
    d2 = load_from_pickle(path_to_d2)
    for k in d2.keys():
        if k in d1.keys():
            d1[k] += d2[k]
        else:
            d1[k] = d2[k]
    save_to_pickle(d1, merged_dict_name)


def create_mapping_dictionaries(d_oc, path_to_dst):
    i = 0
    d_words_id = {}     # word: key
    d_id_words = {}     # key: word
    for r in d_oc.keys():
        d_words_id[r] = i
        i += 1

    for r in d_words_id.keys():
        d_id_words[d_words_id[r]] = r
    save_to_pickle(d_words_id, os.path.join(path_to_dst, "word2index_mapping.pkl"))
    save_to_pickle(d_id_words, os.path.join(path_to_dst, "index2word_mapping.pkl"))


def build_dictionary_occurrences(d, dst):
    """
    Create and save a vocabulary having as keys each of the single words appearing in the mwe, and as values the occurrences of each word
    :param d:
    """
    d_occ = {}
    for k in d.keys():
        w1, w2 = k.split('_')
        for w in [w1, w2]:
            if w in d_occ.keys():
                d_occ[w] += d[k]
            else:
                d_occ[w] = d[k]
    save_to_pickle(d_occ, dst)


def modify_dicts(threshold, dst_dir, occ_dict_path, new_occ_dict_name):
    # Creates modified versions of the current dicts. Only the words occurring more than a certain number of times are kept.
    d_oc = load_from_pickle(occ_dict_path)
    keys_to_remove_from_doc = []
    for k in d_oc.keys():
        if d_oc[k] < threshold:
            keys_to_remove_from_doc.append(k)
    for k in keys_to_remove_from_doc:
        d_oc.pop(k)
    save_to_pickle(d_oc, os.path.join(dst_dir, new_occ_dict_name))
    create_mapping_dictionaries(d_oc, dst_dir)


def main(args):
    paisa_dict_to_merge = args.paisa
    wiki_dict_to_merge = args.wiki
    merged_dict_name = args.merged_dict_name
    occ_dict_name = args.occ_dict
    mapping_dicts_folder = args.mapping_dicts_folder

    merge_dicts(paisa_dict_to_merge, wiki_dict_to_merge, merged_dict_name)
    d = load_from_pickle(merged_dict_name)
    if not occ_dict_name:
        build_dictionary_occurrences(d, '../d_occurrences_numbers.pkl')
    d_oc = load_from_pickle('../d_occurrences_numbers.pkl')

    if not os.path.exists('../word2index_mapping.pkl') or not os.path.exists('../index2word_mapping.pkl'):
        create_mapping_dictionaries(d_oc, mapping_dicts_folder)

    '''modify_dicts(5, 'dicts_5', 'dicts_normal/d_occurrences.pkl', 'd_occurrences.pkl')
    modify_dicts(10, 'dicts_10', 'dicts_normal/d_occurrences.pkl', 'd_occurrences.pkl')
    modify_dicts(15, 'dicts_15', 'dicts_normal/d_occurrences.pkl', 'd_occurrences.pkl')'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--paisa', type=str, required=True, help="Path to the paisa dictionary")
    parser.add_argument('--wiki', type=str, required=True, help="Path to the wikipedia dictionary")
    parser.add_argument('--merged_dict_name', type=str, required=True, help="Path where the merged dictionary will be saved")
    parser.add_argument('--occ_dict', type=str, required=False, help="Path to the occurrences dictionary. If it doesn't exist, don't provide this argument and the program will create the dictionary")
    parser.add_argument('--mapping_dicts_folder', type=str, required=True, help="Path to the folder the mapping dictionaries will be serialized")
    args = parser.parse_args()
    main(args)

