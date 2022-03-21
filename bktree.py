
from Levenshtein import distance as levenshtein_distance
from tqdm import tqdm
from tamil.utf8 import get_letters
from collections import deque
from pprint import pprint, pformat

class BKTree:
    """
    From https://iq.opengenus.org/burkhard-keller-tree/
    """
    def __init__(self, distance_func):
        self._tree = None
        self._distance_func = distance_func

    def add(self, node):
        if self._tree is None:
            self._tree = (node, {})
            return

        current, children = self._tree
        while True:
            dist = self._distance_func(node, current)
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
            dist = self._distance_func(node, candidate)
            if dist <= radius:
                result.append((dist, candidate))

            low, high = dist - radius, dist + radius
            candidates.extend(c for d, c in children.items()
                              if low <= d <= high)
        return result



    
if __name__ == '__main__':

    tree = BKTree(levenshtein_distance)
    with open('../chorkuviyal/output.csv') as f:
        for line in tqdm(f):
            token, count = line.split(',')
            if token:
                tree.add(token)


    with open('tamil_tree_output.txt', 'w') as of:
        of.write(pformat(tree))


    text = input('> ')
    while text:
        pprint(tree.search(text, 2))
        text = input('> ')
