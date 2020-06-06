#** coding: utf-8 **
import os
import sys
import logging
from pprint import pprint, pformat
log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.INFO)

from tqdm import tqdm
from collections import Counter, defaultdict

def count_words(filepath, counter=None):
    if counter == None:
        counter = Counter()

    with open(filepath) as f:
        for line_num, line in enumerate(tqdm(f)):
            try:
                counter.update(line.strip().split())
            except:
                log.exception('=== in line:{}'.format(line_num))

    return counter

def write_counter_tsv(filepath, counter):
    if not counter:
        return
    
    with open(filepath, 'w') as f:
        for word, count in sorted(counter.items(), key=lambda x: -x[1]):
            f.write('{}\t{}\n'.format(word, count))
    

if __name__ == '__main__':
    
    assert len(sys.argv) > 1, 'at least give me a path to input file man!!!'
    in_filepath = sys.argv[1]

    
    if len(sys.argv) > 2:
        out_filepath = sys.argv[2]
    else:
        out_filepath = '{}.vocab.tsv'.format(os.path.basename(in_filepath))


    write_counter_tsv(out_filepath, count_words(in_filepath))
