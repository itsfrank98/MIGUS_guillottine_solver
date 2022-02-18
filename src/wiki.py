import spacy
import os
import json
from utils import write_list_to_file, save_to_pickle
import tqdm
from paisa import build_mwe_dictionaries


def create_conll_rep(src, dst):
    nlp = spacy.load('it_core_news_sm')
    ignore_tags = {"SPACE", "_SP", "SYM"}
    for file in sorted(os.listdir(src)):
        print(file)
        l = []  # List that, for each record stored in the current file being scanned, will contain its conll representation
        for record in tqdm.tqdm(open(os.path.join(src, file), 'rb')):
            record = json.loads(record)
            t = record['text']
            id = record['id']
            title = record['title']
            l.append("<text id = \"" + id + "\" title=\"" + title + "\">\n")
            doc = nlp(t)
            for token in doc:
                if token.tag_ in ignore_tags:
                    continue
                l.append(token.text + " " + token.lemma_ + " " + token.tag_)
            l.append("</text>")
        write_list_to_file(l, dst, file.split('.')[0])


if __name__ == "__main__":
    dir = "../wiki_conll"
    #create_conll_rep('../wiki_json100_uncompressed/', dir)
    d = build_mwe_dictionaries(dir)
    print(len(d.keys()))
    save_to_pickle(d, "../wiki_dict_numbers.pkl")
    # d = load_from_pickle('../wiki_dict.pkl')



