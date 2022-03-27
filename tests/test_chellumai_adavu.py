import argparse
import utils
import csv
from resources import DEFAULT_DICTIONARY_FILES
from pprint import pprint, pformat

from chellumai_adavu import (chellumai_eenu,
                             write_chellumai,
                             read_chellumai,
                             read_tokens,
                             narrukku)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--input',
                        help="frequency dictionary of words",
                        default=','.join(DEFAULT_DICTIONARY_FILES))
    
    parser.add_argument("-o", '--output',
                        help="output file to write chellumai adaivu",
                        default='data/chellumai.csv')
    
    
    args = parser.parse_args()
    pprint(args)
    
    ifilepath = args.input.split(',')
    ofilepath = args.output 
    tokens = []
    for filepath in ifilepath:
        tokens.extend(read_tokens(filepath))

    arichuvadi, chellumai = chellumai_eenu(tokens)
        
    pprint(sorted(arichuvadi))

    # write and read twice to avoid keys() inexistence due to Counter's behavior
    write_chellumai(ofilepath, arichuvadi, chellumai)
    rarichuvadi, rchellumai = read_chellumai(ofilepath)
    
    write_chellumai(ofilepath, rarichuvadi, rchellumai)
    rrarichuvadi, rrchellumai = read_chellumai(ofilepath)

    assert utils.compare_dict(rrchellumai, rchellumai), 'error in read/write'

    pprint(narrukku(arichuvadi, chellumai))
