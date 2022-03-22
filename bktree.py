# -*- coding: utf-8 -*-

from editdistance import eval as levenshtein
from tqdm import tqdm
from tamil.utf8 import get_letters
from collections import deque
from pprint import pprint, pformat

from resources import DEFAULT_DICTIONARY_FILES

class BKTree:
    """
    From https://iq.opengenus.org/burkhard-keller-tree/
    """
    def __init__(self, distance_func):
        self._tree = None
        self._distance_func = distance_func

    def distance_func(self, node, candidate):
        return self._distance_func(node, candidate)
        
    def add(self, node):
        if self._tree is None:
            self._tree = (node, {})
            return

        current, children = self._tree
        while True:
            dist = self.distance_func(node, current)
            target = children.get(dist)
            if target is None:
                children[dist] = (node, {})
                break
            current, children = target

    def search(self, node, radius):
        if self._tree is None:
            return []

        candidates = deque([self._tree])
        result = []
        while candidates:
            candidate, children = candidates.popleft()
            dist = self.distance_func(node, candidate)
            if dist <= radius:
                result.append((dist, candidate))

            low, high = dist - radius, dist + radius
            candidates.extend(c for d, c in children.items()
                              if low <= d <= high)
        return result

class TamilBKTree(BKTree):
    def distance_func(self, node, candidate):
        node, candidate = get_letters(node), get_letters(candidate)
        return super().distance_func(node, candidate)


def build_bktree(filepaths,
                pbarp = False):
    
    tree = TamilBKTree(levenshtein)
    for filepath in filepaths:
        print('loading {}...'.format(filepath))
        if pbarp:
            pbar = tqdm.tqdm(open(filepath), ncols=100)
        else:
            pbar = open(filepath)

        for item in pbar:
            token, count = item.split(',')
            if token:
                tree.add(token)
                if pbarp:
                    pbar.set_description(token)


    return tree

if __name__ == '__main__':

    tree = TamilBKTree(levenshtein)

    for filepath in DEFAULT_DICTIONARY_FILES:
        print('loading {}...'.format(filepath))
        with open(filepath) as f:
            for line in tqdm(f):
                token, count = line.split(',')
                if token:
                    tree.add(token)
                    
    word = input('> ')
    while word:
        pprint('என்ன என்ன வார்த்தைகளோ?')
        pprint(tree.search(word, 2))
        
        word = input('> ')



    with open('tamil_tree_output.txt', 'w') as of:
        of.write(pformat(tree))
