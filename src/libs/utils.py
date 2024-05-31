import numpy as np
import pandas as pd


def safe_divide(a, b):
    return a / b if b != 0 else 0


@np.vectorize
def vectorized_safe_divide(a, b):
    return safe_divide(a, b)

def set_community(sets: list[set]) -> list:
    candidates=sets.copy()
    for i, c in enumerate(candidates):
        for j, c2 in enumerate(candidates):
            if i!=j:
                if len(c.intersection(c2)) >= 1:
                    candidates[i] = c.union(c2)
                    candidates[j] = set()
    candidates=[c for c in candidates if len(c)>0]
    return candidates

def iterative_merge(combinations):
    base=pd.DataFrame(combinations[0])
    for elt in combinations[1:]:
        new=pd.DataFrame(elt)
        index=np.intersect1d(base.columns,new.columns)
        if len(index) == 1:
            index=index[0]
        base=base.set_index(index, drop=True)
        new=new.set_index(index, drop=True)
        base=base.join(new,how='outer')
        base=base.reset_index(drop=False)
    return base.to_dict(orient='records')