#** coding: utf-8 **
import os
import gzip
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

    words = []
    with gzip.open(filepath, 'rt') as f:
        for line_num, line in enumerate(tqdm(f)):
            try:
                word, desc = line.strip().split('|', 1)
                words.append(word)
            except:
                log.exception('=== in line:{}'.format(line_num))

    counter.update(words)
    return counter

def write_counter_tsv(filepath, counter):
    if not counter:
        return
    
    with gzip.open('{}.gz'.format(filepath), 'wt') as f:
        for word, count in sorted(counter.items(), key=lambda x: -x[1]):
            f.write('{}\t{}\n'.format(word, count))
    

if __name__ == '__main__':
    
    assert len(sys.argv) > 1, 'at least give me a path to input file man!!!'
    in_filepath = sys.argv[1]

    
    if len(sys.argv) > 2:
        out_filepath = sys.argv[2]
    else:
        out_filepath = '{}.vocab.tsv'.format( os.path.splitext(in_filepath)[0] )

    write_counter_tsv(out_filepath, count_words(in_filepath))
