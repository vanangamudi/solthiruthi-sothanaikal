#** coding: utf-8 **

import logging
from pprint import pprint, pformat
log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.DEBUG)

from tamil import utf8
from tqdm import tqdm
from collections import Counter, defaultdict
UYIRMEI_MAP_FILEPATH = 'uyir-mei.csv'

def read_uyirmei_map():
    uyirmei_map = {}
    uyirmei_map_reverse = {}
    with open(UYIRMEI_MAP_FILEPATH) as f:
        for line in f.readlines()[1:]:
            letter, mei, uyir = line.strip().split('|')

            if len(uyir) > 0 and len(mei) > 0:
                uyirmei_map[letter] = mei + uyir #not fusing just concat
                uyirmei_map_reverse [mei+uyir] = letter
            elif len(mei) > 0:
                uyirmei_map[letter] = mei
                uyirmei_map_reverse [mei] = letter
            else:
                uyirmei_map[letter] = letter
                uyirmei_map_reverse [letter] = letter


    return uyirmei_map, uyirmei_map_reverse


uyirmei_map, uyirmei_map_reverse = read_uyirmei_map()

def split_uyirmei(string):
    letters = []
    for i in utf8.get_letters(string.strip()):
        if i in uyirmei_map:
            letters.append(uyirmei_map[i])
        else:
            letters.append(i)

    return ''.join(letters)


def build_freqdict(filepath, ngram_size=2, line_limit=100000, offset=1000):
    def ngram_zipper(letters, size=2):
        return [letters[i:] for i in range(size)]

    def ngram_window(letters, start, size=2):
        return ''.join( sletters [ start : start+size ] )
        
    counter = defaultdict(Counter)
    with open(filepath) as f:
        for line in tqdm(f.readlines()[offset:line_limit+offset]):
            for word in line.split():
                oletters = utf8.get_letters(
                    word
                )
                sletters = utf8.get_letters(
                    split_uyirmei(word)
                )

                log.debug('word: {}'.format(word))
                log.debug('len:  oletters/sletters: {}/{}'.format(
                    len(oletters),
                    len(sletters)))
                #print(ngram_zipper(sletters, ngram_size))
                for i, ngram in enumerate(
                        zip(*ngram_zipper(sletters, ngram_size))
                ):
                    
                    window = ngram_window(sletters, i, ngram_size)
                    log.debug(
                        'window: {}, ngram: {}'.format(
                            window,
                            ''.join(ngram)))
                              
                    counter[ window ] [i - len(sletters)] += 1 
                
    return counter


if __name__ == '__main__':
    print(split_uyirmei(
    'போன்றself'
    ))

    freq = build_freqdict(
        filepath = '/home/vanangamudi/data/datasets/text/tamiltext-6M-10lines.txt',
        ngram_size = 3,
        line_limit = 100,
    )
    
    pprint(freq)
    pprint(
        [
            ':'.join(str(j) for j in i) for i in  sorted(
                [(k, sum(v.values())) for k,v in freq.items()],
                key=lambda x: x[1]
            )
        ]
    )



    
