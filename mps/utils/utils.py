from collections import deque

from nltk.tree import Tree


def levelorder(Node, reverse=False):
    """
    BFS tree traversal either from
    left-to-right or right-to-left
    """
    Q = deque()

    Q.append(Node)
    result = []

    while Q:
        current = Q.popleft()
        result.append(current)

        if reverse is True:
            to_traverse = reversed(current)
        else:
            to_traverse = current

        for child in to_traverse:
            if isinstance(child, Tree):
                Q.append(child)

    return result
