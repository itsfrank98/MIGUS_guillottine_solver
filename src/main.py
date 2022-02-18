import os.path
import numpy as np
import math
from utils import load_from_pickle, take_only_dict_relevant_keys
from xml.dom import minidom
import argparse
import time
missing_clues = []


def mutual_information(co_oc, oi, oj, n):
    """
    :param co_oc: Number of co occurrences of the terms oi and oj in the corpus
    :param oi: Number of occurrences of the term oi in the corpus
    :param oj: Number of occurrences of the term oi in the corpus
    :param n: Total number of words in the corpus
    :return:
    """
    e = (oi * oj)/n
    return math.log2(co_oc/e)


def create_clue_array(d, d_oc, clue, d_words_id, k, n):
    """
    Create the array that contains at position j the mutual information between the clue and the word whose ID is j
    :param d: MWE dictionary
    :param d_oc: Occurrences dictionary
    :param clue: Clue
    :param d_words_id: Mapping between a word and an ID. It is used to retrieve the position j of the clue array where the MI between the clue and the word whose ID is j will be put
    :param k: Dimension of the clue array (equal to the number of words in the corpus)
    :param n: Total number of words in the corpus
    :return: Clue array
    """
    ar = np.zeros(k)
    l = [w for w in d.keys() if w.startswith(clue + "_") or w.endswith("_" + clue)]  # Look for all the keys containing the word on the right
    if l:
        oi = d_oc[clue]     # No. of occurrences of the term i
        for key in l:
            key = key.strip()
            wj = key.split('_')[0] if key.split('_')[1] == clue else key.split('_')[1]
            ar[d_words_id[wj]] = mutual_information(d[key], oi, d_oc[wj], n)  # * d[key]
    else:
        missing_clues.append(clue)
    return ar


def build_solution(d, d_oc, clues, d_words_id, d_id_words):
    N = sum(d_oc.values())
    k = len(d_oc.keys())
    out = []
    nz_counter = np.zeros(k)    # Array that at position i will contain the number of nonzero values in the column i of the solution matrix
    matrix = np.zeros((5, k))
    for i in range(5):
        c = clues[i]
        matrix[i] = create_clue_array(d, d_oc, c, d_words_id, k, N)
    for i in range(matrix.shape[1]):
        c = np.count_nonzero(matrix[:, i])
        if c == 5 or c == 4:
            nz_counter[i] = c
    partial_solution = matrix.sum(axis=0)
    solution = np.multiply(partial_solution, nz_counter)
    sorted_indexes = np.argsort(solution)[::-1][:10]
    for e in sorted_indexes:
        out.append(d_id_words[e])
    return out


def run_one_test(clue1, clue2, clue3, clue4, clue5, dicts_src):
    d = load_from_pickle(os.path.join(dicts_src, 'merged_dicts.pkl'))
    d_oc = load_from_pickle(os.path.join(dicts_src, 'd_occurrences.pkl'))
    d = take_only_dict_relevant_keys(d, d_oc, clue1, clue2, clue3, clue4, clue5)
    d_words_id = load_from_pickle(os.path.join(dicts_src, 'word2index_mapping.pkl'))
    d_id_words = load_from_pickle(os.path.join(dicts_src, 'index2word_mapping.pkl'))
    return build_solution(d, d_oc, [clue1, clue2, clue3, clue4, clue5], d_words_id, d_id_words)


def main(args):
    games_path = args.file_path
    dicts_folder = args.dicts_folder
    test_set = minidom.parse(games_path)
    games = test_set.getElementsByTagName('gioco')
    first = 0
    first_5 = 0
    first_10 = 0
    reciprocal_ranks = []  # Reciprocal rank
    game_counter = 0
    for game in games:
        game_counter += 1
        id = game.getElementsByTagName("id")[0].firstChild.data
        clue1 = game.getElementsByTagName("def1")[0].firstChild.data
        clue2 = game.getElementsByTagName("def2")[0].firstChild.data
        clue3 = game.getElementsByTagName("def3")[0].firstChild.data
        clue4 = game.getElementsByTagName("def4")[0].firstChild.data
        clue5 = game.getElementsByTagName("def5")[0].firstChild.data
        solution = game.getElementsByTagName("sol")[0].firstChild.data.lower()
        predicted_solutions = run_one_test(clue1.lower(), clue2.lower(), clue3.lower(), clue4.lower(), clue5.lower(), dicts_folder)
        print("\nId: {}".format(id))
        if solution in predicted_solutions:
            first_10 += 1
            index = predicted_solutions.index(solution) + 1
            reciprocal_ranks.append(1/index)
            if index <= 5:
                first_5 += 1
                if index == 1:
                    first += 1
        else:
            reciprocal_ranks.append(0)
        print("Solution: {}".format(solution))
        print(predicted_solutions)

    print("Top 1: {}".format(first))
    print("Top 5: {}".format(first_5))
    print("Top 10: {}\n".format(first_10))

    print("Precision @1: {}".format(first/game_counter))
    print("Precision @5: {}".format(first_5/game_counter))
    print("Precision @10: {}".format(first_10/game_counter))
    print("MRR: {}".format(np.mean(np.asarray(reciprocal_ranks))))
    print("Coverage of clues: {}".format(((5*game_counter)-len(missing_clues))/(5*game_counter)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hints", nargs=5, type=str, required=False)
    parser.add_argument("--file_path", type=str, required=False, help="Path to the XML file containing the test set")
    parser.add_argument("--dicts_folder", type=str, required=True, help="Path to the folder containing the dictionaries to use")
    args = parser.parse_args()
    hints = args.hints
    if hints:
        now = time.time()
        print("I'm trying to solve the game...")
        solutions = run_one_test(hints[0].lower(), hints[1].lower(), hints[2].lower(), hints[3].lower(), hints[4].lower(), args.dicts_folder)
        print("Hints you provided:")
        for h in hints:
            print("   {}".format(h))
        print("\nMy top 10 solutions are:".format(solutions))
        for s in solutions:
            print("   {}".format(s))
        print("\nIt took me about {} seconds to come up with my solution".format(int(time.time()-now)))
    else:
        # COMMAND: python src/main.py --file_path test/evalita.xml --dicts_folder dicts_normal
        main(args)

