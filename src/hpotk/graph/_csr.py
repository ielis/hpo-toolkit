import typing

import numpy as np
import numpy.typing as npt

from ._api import OntologyGraph, NODE


class CsrOntologyGraph(OntologyGraph):

    # TODO - implement!

    @property
    def root(self) -> NODE:
        raise NotImplemented('Not yet implemented')

    def get_children(self, source: NODE) -> typing.Iterator[NODE]:
        raise NotImplemented('Not yet implemented')

    def get_parents(self, source: NODE) -> typing.Iterator[NODE]:
        raise NotImplemented('Not yet implemented')

    def __contains__(self, item: NODE) -> bool:
        raise NotImplemented('Not yet implemented')

    def __iter__(self) -> typing.Iterator[NODE]:
        raise NotImplemented('Not yet implemented')
