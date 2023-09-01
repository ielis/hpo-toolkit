import time
import unittest

import numpy as np

from ._term_id import SimpleTermId, DefaultTermId


@unittest.skip('The bench is not run routinely.')
class TestTermIdBench(unittest.TestCase):
    """
    A naive benchmark to compare time required to create a set from different TermId implementations.
    """

    def test_bench_create_set(self):
        n_iter = 10
        n_elements = 10_000
        n_concepts = 1_000_000

        corpus = np.array(['HP:' + str(i).rjust(7, '0') for i in range(n_concepts)])
        simple = np.fromiter(map(lambda curie: SimpleTermId(curie, 2), corpus), dtype=object)
        default = np.fromiter(map(lambda curie: DefaultTermId(curie, 2), corpus), dtype=object)

        simple_elapsed = []
        default_elapsed = []
        for _ in range(n_iter):
            idx = np.random.choice(n_concepts, size=n_elements, replace=True)
            simple_sel = simple[idx]
            elapsed = time_it(set, simple_sel)
            simple_elapsed.append(elapsed)

            default_sel = default[idx]
            elapsed = time_it(set, default_sel)
            default_elapsed.append(elapsed)

        s = np.array(simple_elapsed) / 1e6  # To convert to ms
        d = np.array(default_elapsed) / 1e6  # To convert to ms

        print(f'Simple: {s.mean():.3f} ±{s.std():.3f}ms')
        print(f'Default: {d.mean():.3f} ±{d.std():.3f}ms')


def time_it(f, *args):
    start = time.time_ns()
    f(*args)
    return time.time_ns() - start
