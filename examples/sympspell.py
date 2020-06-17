import sys
sys.path.append('..')

from symspellpy import SymSpell, Verbosity

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
sym_spell.load_dictionary('../data/etymdict.csv.vocab.tsv.gz',
                          term_index=0,
                          count_index=1,
                          separator="\t")

def check(input_term):
    suggestions = sym_spell.lookup(input_term, Verbosity.CLOSEST,
                                   max_edit_distance=2,
                                   include_unknown=True)
    for suggestion in suggestions:
        print(suggestion)

        
while True:
    input_term = input('> ').strip()  # misspelling of "apostrophe"

    if not input_term:
        break

    check(input_term)
