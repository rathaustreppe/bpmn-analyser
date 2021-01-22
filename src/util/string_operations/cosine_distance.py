


def cosine_distance(word1: str, word2: str) -> float:
    # algorithm for calculating distance of two strings
    # Example: Word1 == Word2 == 'hello' --> score: 1.0, means exact
    # Example: Word1 == 'abc', Word2 == 'xyz' --> score: 0.0
    # Example: Word1 == 'ready', Word2 == 'reedy' --> score: 0.9
    set1 = {w for w in word1}
    set2 = {w for w in word2}

    l1 = []
    l2 = []

    # form a set containing keywords of both strings
    rvector = set1.union(set2)
    for w in rvector:
        if w in set1:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in set2:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    cosine = round(cosine, 2)
    return cosine