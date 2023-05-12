import abc
import typing
import warnings

import numpy as np
from collections import deque


class ShapedMixin(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def shape(self):
        pass


class CsrMatrixBuilder(ShapedMixin):
    """
    The builder has been deprecated due to poor performance and will be removed in v1.0.0.
    """

    def __init__(self, shape: typing.Tuple[int, int]):
        _check_shape(shape)
        self._shape = shape
        self._row = np.zeros(shape=(shape[0] + 1,), dtype=int)
        self._col = deque([])
        self._data = deque([])
        warnings.warn('CsrMatrixBuilder has been deprecated and will be removed in v1.0.0',
                      DeprecationWarning, stacklevel=2)

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if len(key) == 2:
                qrow, qcol = key
                _check_bounds(qrow, qcol, self._shape)

                start, end = self._row[qrow: qrow + 2]

                col_idx_adjustment, value_will_be_updated = 0, False  # Loop variables
                for i, col in enumerate(self._col):
                    # We iterate over all entries of the _indices deque since we cannot slice the deque
                    if start > i:
                        # Let's discard the first [0..row-1] rows.
                        continue
                    if i >= end:
                        # No need to iterate over the rows beyond the target row.
                        break

                    # Here we are at the relevant part of the `self._indices`.
                    # We determine if we need to update an existing value,
                    # or create a new entry at an approperiate place
                    if col < qcol:
                        col_idx_adjustment += 1
                        continue
                    elif col == qcol:
                        value_will_be_updated = True

                    break

                idx = start + col_idx_adjustment

                if value_will_be_updated:
                    self._data[idx] = value
                else:
                    # We are adding a new entry, so we must increment relevant _indptr entries
                    mask = np.arange(self._row.shape[0]) > qrow
                    self._row[mask] += 1
                    self._col.insert(idx, qcol)
                    self._data.insert(idx, value)

            else:
                raise ValueError(f'Setting {len(key)} dimensions but only 2D indexing is supported')
        else:
            raise IndexError(f'Unknown index type {type(key)}')

    @property
    def shape(self):
        return self._shape

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"CsrMatrixBuilder(shape={self._shape}, indptr={self._row}, indices={self._col}, data={self._data})"


class ImmutableCsrMatrix(ShapedMixin):

    def __init__(self, row: typing.Sequence,
                 col: typing.Sequence,
                 data: typing.Sequence,
                 shape: typing.Tuple[int, int],
                 dtype=float):
        # Sanity checks
        _check_sequence_of_nonnegative_ints('row', row)
        _check_sequence_of_nonnegative_ints('col', col)
        if not isinstance(data, typing.Sequence):
            raise ValueError(f'data must be a sequence but was {type(type(data))}')

        _check_shape(shape)

        if len(row) - 1 != shape[0]:
            raise ValueError(f'row len {len(row) - 1} must be equal to number of rows {shape[0]}')

        if not isinstance(dtype, type):
            raise ValueError(f'dtype must be a type but was {type(dtype)}')

        # Store the state in numpy arrays
        self._row = np.array(row)
        self._col = np.array(col)
        self._data = np.array(data)
        self._shape = shape
        self._dtype = dtype
        self._default = self._default_for_dtype(dtype)

    def __getitem__(self, item):
        if isinstance(item, int):
            if 0 <= item < self._shape[0]:
                start_row, end_row = self._row[item: item + 2]
                row = np.full(shape=(self._shape[1],),
                              fill_value=self._default,
                              dtype=self._dtype)
                if start_row != end_row:
                    idxs = self._col[start_row: end_row]
                    vals = self._data[start_row: end_row]
                    row[idxs] = vals
                return row
            else:
                if 0 > item:
                    raise ValueError(f'Requested row #{item} but negative indexing is not supported')
                else:
                    raise IndexError(f'Row index {item} out of bounds for a {self._shape} matrix')
        elif isinstance(item, tuple):
            if len(item) == 2:
                qrow, qcol = item
                _check_bounds(qrow, qcol, self._shape)
                # +2 is safe since we check bounds above and self._indptr has n+1 elements for n x m matrix.
                start_row, end_row = self._row[qrow: qrow + 2]
                for i, col_idx in enumerate(self._col[start_row: end_row]):
                    if col_idx == qcol:
                        return self._data[start_row + i]
                return self._default
            else:
                raise ValueError(f'Requesting {len(item)} dimensions but only 2D indexing is supported')
        else:
            raise IndexError(f'Unknown index type {type(item)}')

    def col_indices_of_val(self, row: int, query):
        """
        Return indices of columns with matching query value in a given row.

        Raises IndexError if `row` is out of bounds.
        """
        if not (isinstance(row, int) and 0 <= row < self._shape[0]):
            raise IndexError(f'row must be an int in range [0, {self.shape[0]}) but was {row}')

        start_row, end_row = self._row[row: row + 2]
        value_idxs = self._col[start_row: end_row]
        if query == self._default:
            # We do not store indices of the default value in the matrix
            col_indices = np.arange(self._shape[1])
            row_mask = np.full(fill_value=True, shape=(self._shape[1],), dtype=bool)
            if len(value_idxs) != 0:
                row_mask[value_idxs] = False
                return col_indices[row_mask]
            else:
                return col_indices
        else:
            # We're getting indices of columns where data is equal to the query
            row_mask = self._data[start_row: end_row] == query
            return value_idxs[row_mask]

    @property
    def shape(self):
        return self._shape

    @staticmethod
    def _default_for_dtype(dtype):
        if dtype == float:
            return 0.
        elif dtype == int:
            return 0
        elif dtype == bool:
            return False


def _check_shape(shape):
    if not (isinstance(shape, tuple) and len(shape) == 2):
        raise ValueError(f'shape must be a tuple with two non-negative ints')
    _check_sequence_of_nonnegative_ints('shape', shape)


def _check_bounds(row, col, shape):
    # Check bounds
    if not (0 <= row < shape[0]):
        raise IndexError(f'Row index {row} out of bounds for a {shape} matrix')
    if not (0 <= col < shape[1]):
        raise IndexError(f'Column index {col} out of bounds for a {shape} matrix')


def _check_sequence_of_nonnegative_ints(name, vals):
    if not (isinstance(vals, (typing.Sequence, np.ndarray)) and all([val >= 0 for val in vals])):
        raise ValueError(f'{name} must be a sequence of ints')
