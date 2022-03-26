# -*- coding: utf-8 -*-
from bloom_filter import BloomFilter
from random import shuffle
from tqdm import tqdm
import tqdm

import utils
from resources import DEFAULT_DICTIONARY_FILES

BLOOMFILTER_SIZE = 200000 #no of items to add
BLOOMFILTER_PROB = 0.05 #false positive probability


def build_bloom(filepaths,
                size  = BLOOMFILTER_SIZE,
                prob  = BLOOMFILTER_PROB,
                pbarp = False):
    
    bloom = BloomFilter(size, prob)

    for filepath in filepaths:
        print('loading {}...'.format(filepath))
        if pbarp:
            pbar = tqdm.tqdm(utils.openfile(filepath), ncols=100)
        else:
            pbar = utils.openfile(filepath)

        for item in pbar:
            token, count = item.split(',')
            if token:
                bloom.add(token)
                if pbarp:
                    pbar.set_description(token)


    return bloom

if __name__ == '__main__':
    bloom = build_bloom(DEFAULT_DICTIONARY_FILES)
    word = input('> ')
    while word:
        print('இருக்குதா? {}'.format('இருக்கு' if word in bloom else 'இல்லை'))
        word = input('> ')
