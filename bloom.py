from bloom_filter import BloomFilter
from random import shuffle
from tqdm import tqdm
import tqdm

BLOOMFILTER_SIZE = 200000 #no of items to add
BLOOMFILTER_PROB = 0.05 #false positive probability


def build_bloom(filepath, pbarp=False):
    bloom = BloomFilter(BLOOMFILTER_SIZE, BLOOMFILTER_PROB)
    if pbarp:
        pbar = tqdm.tqdm(open(filepath), ncols=100)
    else:
        pbar = open(filepath)
        
    for item in pbar:
        token, count = item.split(',')
        if token:
            bloom.add(token)
            if pbarp:
                pbar.set_description(token)


    return bloom

if __name__ == '__main__':
    bloom = build_bloom('../chorkuviyal/output.csv')
    word = input('> ')
    while word:
        print('word present? {}'.format(
            word in bloom))
        word = input('> ')
