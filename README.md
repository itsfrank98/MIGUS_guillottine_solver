# MIGUS_guillottine_solver
This system depicts an artificial player for the TV Italian language game "La ghigliottina". A detailed description of the system is reported in **report.tex**
<br>
## Links for downloading the corpora: 
PAISà: https://clarin.eurac.edu/repository/xmlui/handle/20.500.12124/3 <br>
WIKIPEDIA DUMP: http://itwiki-20220101-pages-articles-multistream.xml.bz2

### Wikiextractor tool: 
https://github.com/attardi/wikiextractor

#### How to use Wikiextractor:
- Go in the repo where you downloaded the wikipedia dump
- Run the following command to extract the dump in files large 500MB each, in the "wiki_json" folder, in json format: **wikiextractor -cb 500M --json --no-templates -o wiki_json itwiki-latest-pages-articles.xml.bz2**

### Create corpus
- Put the PAISA and WIKI files in a folder in the same directory where the SRC folder is (I splitted the PAISA corpus in multiple files otherwise it wouldn't fit in my RAM)
- Run the src/paisa.py and src/wiki.py

### Create dictionaries
Here you merge the dictionaries created for paisa and wiki into a single one, and also create supporting dictionaries that will be used to solve the games <br>
Run the command **python src/create_dictionaries.py --paisa path_to_your_processed_paisa --wiki path_to_your_processed_wiki --merged_dict_name path_where_you_want_to_save_the_merged_dictionaries --mapping_dicts_folder folder_where_the_supporting_dictionaries_will_be_put**

### Solving the game
If you want to solve a single game run, providing 5 clues (suppose the clues are _difendere_, _temperatura_, _tempo_, _tasto_, _assoluto_), run:
**python src/main.py --hints difendere temperatura tempo tasto assoluto --dicts_folder folder_where_the_supporting_dictionaries_are**

If you want to evaluate the system on a test set containing some game instances along with their actual results (suppose you want to test on the test set **test/evalita.xml**) run the command: **python src/main.py --file_path test/evalita.xml --dicts_folder folder_where_the_supporting_dictionaries_are**4

It will print, for each game, the proposed solutions and at the end it will compute the P@1, P@5, P@10, MRR vallues. You can copy them in a file

