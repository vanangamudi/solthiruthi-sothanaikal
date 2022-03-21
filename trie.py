# -*- coding: utf-8 -*-
from pprint import pprint, pformat
import pdb

class Node(object):

    def __repr__(self):
        return "Node({}, {}, {})\n{}".format(
            self.value,
            self.children,
            self.is_complete,
            ' ' * self.level)

    def __str__(self):
        return self.__repr__()

    def __init__(self, value=None, level=0):
        self.value = value
        self.count = 0
        self.children = {}
        self.is_complete = False
        self.level = level
        

class Trie(object):

    def __init__(self):
        self.root = Node(value=None, level=0)

    def __repr__(self):   return self.root.__repr__()
    def __str__(self):    return self.__repr__()

    def add(self, item):
        node, i = self.find_prefix(item)
        if i < len(item):
            while i < len(item):
                new_node = Node(item[:i+1], level=i+1)
                node.children[item[i]] = new_node
                node = new_node
                i += 1

            node.is_complete = True

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
        if node:
            return node.is_complete

    def get_all_suffixes(self, prefix):
        pdb.set_trace()
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

if __name__ == '__main__':
    trie = Trie()
    trie.add("hell")
    trie.add("hello")
    trie.add("hey")
    trie.add("trie")
    pprint (trie)
    pprint (trie.find_prefix("hey"))
    pprint (trie.get_all_suffixes("h"))
