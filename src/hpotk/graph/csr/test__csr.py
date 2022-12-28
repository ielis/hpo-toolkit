import unittest

from collections import namedtuple

import ddt

from ._csr import *

CsrData = namedtuple('CsrData', ['indptr', 'indices', 'data', 'shape'])


@ddt.ddt
class TestImmutableCsrMatrix(unittest.TestCase):

    # [[100 102 104 106]
    #  [108 110 112 114]
    #  [116 118 120 122]
    #  [124 126 128 130]]
    FULL = CsrData(
        indptr=[0, 4, 8, 12, 16],
        indices=[0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3],
        data=[100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128, 130],
        shape=(4, 4))

    # [[1. 0. 0. 2.]
    #  [0. 3. 0. 0.]
    #  [0. 0. 4. 0.]
    #  [5. 0. 0. 6.]]
    ALL_EDGES = CsrData(
        indptr=[0, 2, 3, 4, 6],
        indices=[0, 3, 1, 2, 0, 3],
        data=[1., 2., 3., 4., 5., 6.],
        shape=(4, 4))

    # [[0. 0. 0.]
    #  [0. 0. 0.]
    #  [0. 0. 0.]]
    ZEROES = CsrData(
        indptr=[0, 0, 0, 0],
        indices=[],
        data=[],
        shape=(3, 3))

    # [[0. 1. 0. 2.]
    #  [3. 0. 4. 5.]]
    RECT = CsrData(
        indptr=[0, 2, 5],
        indices=[1, 3, 0, 2, 3],
        data=[1., 2., 3., 4., 5.],
        shape=(2, 4))

    @ddt.data(
        (0, 0, 100), (0, 1, 102), (0, 2, 104), (0, 3, 106),
        (1, 0, 108), (1, 1, 110), (1, 2, 112), (1, 3, 114),
        (2, 0, 116), (2, 1, 118), (2, 2, 120), (2, 3, 122),
        (3, 0, 124), (3, 1, 126), (3, 2, 128), (3, 3, 130))
    @ddt.unpack
    def test_full(self, row, col, val):
        mat = make_csr_matrix(TestImmutableCsrMatrix.FULL)
        self.assertEqual(val, mat[row, col])

    @ddt.data(
        (0, 0, 1.), (0, 1, 0.), (0, 2, 0.), (0, 3, 2.),
        (1, 0, 0.), (1, 1, 3.), (1, 2, 0.), (1, 3, 0.),
        (2, 0, 0.), (2, 1, 0.), (2, 2, 4.), (2, 3, 0.),
        (3, 0, 5.), (3, 1, 0.), (3, 2, 0.), (3, 3, 6.))
    @ddt.unpack
    def test_all_edges(self, row, col, val):
        mat = make_csr_matrix(TestImmutableCsrMatrix.ALL_EDGES)
        self.assertEqual(val, mat[row, col])

    def test_zeros(self):
        zeros = make_csr_matrix(TestImmutableCsrMatrix.ZEROES)
        for i in range(zeros.shape[0]):
            for j in range(zeros.shape[1]):
                self.assertEqual(0., zeros[i, j])

    def test_shapes(self):
        self.assertEqual((4, 4), make_csr_matrix(TestImmutableCsrMatrix.FULL).shape)
        self.assertEqual((4, 4), make_csr_matrix(TestImmutableCsrMatrix.ALL_EDGES).shape)
        self.assertEqual((3, 3), make_csr_matrix(TestImmutableCsrMatrix.ZEROES).shape)
        self.assertEqual((2, 4), make_csr_matrix(TestImmutableCsrMatrix.RECT).shape)

    @ddt.data(
        (0, [100, 102, 104, 106]),
        (1, [108, 110, 112, 114]),
        (2, [116, 118, 120, 122]),
        (3, [124, 126, 128, 130]))
    @ddt.unpack
    def test_get_row__full(self, i, vals):
        mat = make_csr_matrix(TestImmutableCsrMatrix.FULL)
        assert np.allclose(mat[i], np.array(vals))

    @ddt.data(
        (0, [0., 0., 0.]),
        (1, [0., 0., 0.]),
        (2, [0., 0., 0.]))
    @ddt.unpack
    def test_get_row__zeroes(self, i, vals):
        mat = make_csr_matrix(TestImmutableCsrMatrix.ZEROES)
        assert np.allclose(mat[i], np.array(vals))

    @ddt.data(
        (0, [1., 0., 0., 2.]),
        (1, [0., 3., 0., 0.]),
        (2, [0., 0., 4., 0.]),
        (3, [5., 0., 0., 6.]))
    @ddt.unpack
    def test_get_row__all_edges(self, i, vals):
        mat = make_csr_matrix(TestImmutableCsrMatrix.ALL_EDGES)
        assert np.allclose(mat[i], np.array(vals))

    def test_col_indices_of_val(self):
        edges = make_csr_matrix(TestImmutableCsrMatrix.ALL_EDGES)
        assert np.allclose(edges.col_indices_of_val(0, 0.), [1, 2])
        assert np.allclose(edges.col_indices_of_val(0, 1.), [0])
        assert np.allclose(edges.col_indices_of_val(0, 2.), [3])
        assert np.allclose(edges.col_indices_of_val(0, 3.), [])

        zeroes = make_csr_matrix(TestImmutableCsrMatrix.ZEROES)
        assert np.allclose(zeroes.col_indices_of_val(0, 0.), [0, 1, 2])
        assert np.allclose(zeroes.col_indices_of_val(0, 1.), [])

        full = make_csr_matrix(TestImmutableCsrMatrix.FULL)
        assert np.allclose(full.col_indices_of_val(0, 0), [])
        assert np.allclose(full.col_indices_of_val(0, 100), [0])
        assert np.allclose(full.col_indices_of_val(0, 102), [1])


def make_csr_matrix(example: CsrData):
    return ImmutableCsrMatrix(example.indptr, example.indices, example.data, example.shape)


class TestCsrMatrixBuilder(unittest.TestCase):

    def test_incremental(self):
        builder = CsrMatrixBuilder(shape=(3, 3))
        builder[0, 0] = 1.
        builder[0, 1] = 2.
        builder[0, 2] = 3.

        builder[1, 0] = 4.
        builder[1, 1] = 5.
        builder[1, 2] = 6.

        builder[2, 0] = 7.
        builder[2, 1] = 8.
        builder[2, 2] = 9.

        assert np.allclose(builder.row, np.array([0, 3, 6, 9]))
        assert np.allclose(builder.col, np.array([0, 1, 2, 0, 1, 2, 0, 1, 2]))
        assert np.allclose(builder.data, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]))

    def test_decrement(self):
        builder = CsrMatrixBuilder(shape=(3, 3))
        builder[2, 2] = 9.
        builder[2, 1] = 8.
        builder[2, 0] = 7.

        builder[1, 2] = 6.
        builder[1, 1] = 5.
        builder[1, 0] = 4.

        builder[0, 2] = 3.
        builder[0, 1] = 2.
        builder[0, 0] = 1.

        assert np.allclose(builder.row, np.array([0, 3, 6, 9]))
        assert np.allclose(builder.col, np.array([0, 1, 2, 0, 1, 2, 0, 1, 2]))
        assert np.allclose(builder.data, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]))
