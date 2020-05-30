#** coding: utf-8 **

from tamil import utf8
from tqdm import tqdm
from pprint import pprint, pformat
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


def build_freqdict(filepath, line_limit=1000):
    counter = defaultdict(Counter)
    with open(filepath) as f:
        for line in tqdm(f.readlines()[:line_limit]):
            for word in line.split():
                rword = list(reversed(
                    utf8.get_letters(
                        split_uyirmei(word))))
                for i, (p, q, r, s) in enumerate(
                        zip(rword, rword[1:], rword[2:], rword[3:])
                ):

                    window = ''.join(reversed(
                        list( reversed(word) ) [ i : (i+1)*4 ]
                    ))
                    counter[ window ] [i] += 1 
                
    return counter


if __name__ == '__main__':
    print(split_uyirmei(
    'போன்றself'
    ))

    freq = build_freqdict('/home/vanangamudi/data/datasets/text/tamiltext-6M-10lines.txt')
    pprint(freq)
