# -*- coding: utf-8 -*-
from pprint import pprint, pformat
import pdb
from tqdm import tqdm
from tamil.utf8 import get_letters

from resources import DEFAULT_DICTIONARY_FILES
from profiling import memory_usage

import argparse

DEBUG = True

class Node(object):

    def __repr__(self):
        if self.level < 160:
            return "Node({}, {}, {})\n{} {}".format(
                ''.join(self.value) if self.value else self.value,
                self.count,
                self.is_complete,
                '\t' * self.level,
                self.children,)
        else:
            return ''

    def __str__(self):
        return self.__repr__()

    def __init__(self, value=None, count=1, level=0):
        self.value = value
        self.count = count
        self.children = {}
        self.is_complete = False
        self.level = level
        

class Trie(object):

    def __init__(self):
        self.root = Node(value=None, level=0)
        self._count = 0
        
    def __repr__(self):   return self.root.__repr__()
    def __str__(self):    return self.__repr__()

    def add(self, item):
        node, i = self.find_prefix(item)
        if i < len(item):
            #increment count
            j = 0
            tnode = self.root
            while j < i:
                tnode.children[item[j]].count += 1
                tnode = tnode.children[item[j]]
                j += 1
                
            # add new nodes
            while i < len(item):
                #new_node = Node(item[:i+1], count=1, level=i+1)
                #new_node = Node(item[i], count=1, level=i+1)
                new_node = Node(None, count=1, level=i+1)
                node.children[item[i]] = new_node
                node = new_node
                i += 1

            node.is_complete = True
            self._count += 1
            
    def find_prefix(self, prefix, default=None):
        i = 0
        prev_node = node = self.root
        while i < len(prefix) and node:
            prev_node = node
            node = node.children.get(prefix[i], None)
            i += 1
            
        if i <= len(prefix):
            return prev_node, i-1
        else:
            return self.root, 0
        
    def prefix_exists_p(self, prefix):
        node, index = self.find_prefix(prefix)
        if not node == self.root:
            node = node.children.get(prefix[-1], None)
            if node:
                return node.is_complete

    def get_all_suffixes(self, prefix):

        suffixes = []
        node, level = self.find_prefix(prefix)
        if len(prefix):
            node = node.children[prefix[-1]]
        branches = list([ ('' + k, v) for k,v in node.children.items()])
        while branches:
            prefix, node = branches.pop(0)
            branches = list([ (prefix + k, v) for k,v in node.children.items()]) + branches
            if node.is_complete:
                suffixes.append(prefix)

        return suffixes

    def words(self):
        return self.get_all_suffixes(self.root)

def build_trie(filepaths,
                pbarp = False):
    
    trie = Trie()
    for filepath in filepaths:
        print('loading {}...'.format(filepath))
        if pbarp:
            pbar = tqdm.tqdm(open(filepath), ncols=100)
        else:
            pbar = open(filepath)

        for item in pbar:
            token, count = item.split(',')
            if token:
                trie.add(get_letters(token))
                if pbarp:
                    pbar.set_description(token)


    return trie

def dummy_test():
    trie = Trie()
    trie.add("hell")
    trie.add("hello")
    trie.add("hey")
    trie.add("trie")
    pprint (trie)
    pprint (trie.find_prefix("hey"))
    pprint (trie.get_all_suffixes("h"))
    pprint (trie.prefix_exists_p("hel"))
    pprint (trie.prefix_exists_p("hell"))
    pprint (trie.prefix_exists_p("heyl"))
    pprint (trie.prefix_exists_p("hey"))
    pprint (trie.prefix_exists_p("tri"))
    pprint (trie.prefix_exists_p("trie"))
    pprint (trie.prefix_exists_p("Trie"))

if __name__ == '__main__':


    print('memory usage: {}'.format(memory_usage()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='debugging flag')
    parser.add_argument('--debug-wordcount',
                        default=0,
                        type=int,
                        help='debugging flag')
        
    parser.add_argument('--filepaths', 
                        default=DEFAULT_DICTIONARY_FILES,
                        help='comma separated filepaths')
    
    args = parser.parse_args()
    pprint(args)
    print('memory usage: {}'.format(memory_usage()))

    tamil_trie = Trie()
    for filepath in args.filepaths:
        print('loading {}...'.format(filepath))
        with open(filepath) as f:
            for line in tqdm(f):
                token, count = line.split(',')
                if token:
                    tamil_trie.add(get_letters(token))

                if args.debug:
                    if args.debug_wordcount and tamil_trie._count >= args.debug_wordcount:
                        break

    print('built trie...')
    print('memory usage: {}'.format(memory_usage()))
    word = input('> ')
    while word:
        print('இருக்குதா? {}'.format(
            'இருக்கு' if tamil_trie.prefix_exists_p(get_letters(word)) \
            else 'இல்லை'))
        
        word = input('> ')


    with open('tamil_trie_output.txt', 'w') as of:
        of.write(pformat(tamil_trie))
