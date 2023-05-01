import csv
import datetime
import functools
import logging
import re
import typing
from collections import defaultdict

from hpotk.model import MetadataAware
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from hpotk.util import open_text_io_handle_for_writing, open_text_io_handle_for_reading
from .._traversal import get_descendants, get_ancestors, get_children
from ._ic import AnnotationIcContainer

# implement Resnik IC computation starting from a collection of world documents
# and see if we can plug in excluded into the values.

HPO_PATTERN = re.compile(r"HP:(?P<ID>\d{7})")

logger = logging.getLogger('hpotk.algorithm.similarity')


class SimilarityContainer(MetadataAware, typing.Sized):
    """
    A container for pre-calculated semantic similarity results.
    """

    def __init__(self, metadata: typing.Optional[typing.Mapping[str, str]] = None):
        self._meta = dict()
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError(f'meta must be a dict but was {type(metadata)}')
            else:
                self._meta.update(metadata)
        self._data = self._prepare_datadict()

    def get_similarity(self, a: str, b: str) -> float:
        """
        Get similarity of two entries `a` and `b`.

        :param a: an item, e.g. `HP:1234567`
        :param b: another item, e.g. `HP:9876543`
        :return: a non-negative semantic similarity
        """
        o, i = (a, b) if a <= b else (b, a)
        outer = self._data.get(o, None)
        if outer:
            return outer.get(i, 0.)
        else:
            return 0.

    def set_similarity(self, a: str, b: str, sim: float):
        """
        Set semantic similarity for items `a` and `b`.
        :param a: an item, e.g. `HP:1234567`
        :param b: another item, e.g. `HP:9876543`
        :param sim: a non-negative semantic similarity
        """
        if sim < 0.:
            raise ValueError(f'Similarity must be non-negative: {sim}')
        if a <= b:
            self._data[a][b] = sim
        else:
            self._data[b][a] = sim

    def items(self):
        """
        Get a generator of semantic similarities.

        Each item is a tuple with three items:
        *  left item (`str`)
        * right item (`str`)
        * similarity (`float`)
        """
        for a, vals in self._data.items():
            for b, sim in vals.items():
                yield a, b, sim

    @property
    def metadata(self) -> typing.Mapping[str, str]:
        return self._meta

    @staticmethod
    def _prepare_datadict() -> typing.MutableMapping[str, typing.MutableMapping[str, float]]:
        def inner() -> float:
            return 0.

        def outer() -> defaultdict:
            return defaultdict(inner)

        return defaultdict(outer)

    def to_csv(self, fh: typing.Union[str, typing.IO]):
        now = datetime.datetime.now()
        self._meta['created'] = now.strftime('%Y-%m-%d-%H:%M:%S')
        with open_text_io_handle_for_writing(fh) as handle:
            # (0) Comments
            handle.write('#Information content of the most informative common ancestor for term pairs\n')
            handle.write('#' + self.metadata_to_str() + '\n')

            # (1) Header
            fieldnames = ['term_a', 'term_b', 'ic_mica']
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()

            # (2) Entries
            for left, right, sim in self.items():
                writer.writerow({'term_a': left, 'term_b': right, 'ic_mica': sim})

    @staticmethod
    def from_csv(fh: typing.Union[str, typing.IO]):
        header = []
        records = []

        def store_header(row: str) -> bool:
            if row[0] == '#':
                header.append(row)
                return False
            return True

        with open_text_io_handle_for_reading(fh) as handle:
            reader = csv.DictReader(filter(store_header, handle))
            for record in reader:
                records.append((record['term_a'], record['term_b'], float(record['ic_mica'])))

        meta = SimilarityContainer._parse_meta(header)
        data = SimilarityContainer(meta)
        for record in records:
            data.set_similarity(record[0], record[1], record[2])

        return data

    @staticmethod
    def _parse_meta(header: typing.Sequence[str]) -> typing.Mapping[str, str]:
        # Poor man's parsing.
        if len(header) < 2 or len(header[1]) < 2:
            return {}
        else:
            # The 2nd line is the metadata line, and we strip off the first and the last char (# and \n)
            return MetadataAware.metadata_from_str(header[1][1:-1])

    def __len__(self) -> int:
        return sum([len(inner) for inner in self._data.values()])


def _get_common_ancestors(hpo: MinimalOntology,
                          left: TermId,
                          right: TermId) -> frozenset[TermId]:
    la = get_ancestors(hpo, left, include_source=True)
    ra = get_ancestors(hpo, right, include_source=True)
    return la.intersection(ra)


def precalculate_resnik_similarity_for_hpo(ic: AnnotationIcContainer,
                                           hpo: MinimalOntology) -> SimilarityContainer:
    """
    Precalculate Resnik semantic similarity for :class:`TermId` pairs.

    :param ic: a mapping for obtaining an information content of a :class:`TermId`.
    :param hpo: HPO ontology.
    :return: a mapping with Resnik similarity for :class:`TermId` pairs where the similarity :math:`s>0`.
    """
    metadata = {'hpo_version': hpo.version}
    metadata.update(ic.metadata)
    data = SimilarityContainer(metadata=metadata)
    groups = list(get_children(hpo, PHENOTYPIC_ABNORMALITY))
    count = 0
    for section_top in groups:
        term = hpo.get_term(section_top)
        term_ids = list(get_descendants(hpo, section_top, include_source=True))
        logger.info(f'Calculating for {term.name} with {len(term_ids) - 1} descendants')
        for i in range(len(term_ids)):
            left = term_ids[i]
            for j in range(i, len(term_ids)):
                right = term_ids[j]

                ic_mica = functools.reduce(max,
                                           map(lambda term_id: ic.get(term_id, 0.),
                                               _get_common_ancestors(hpo, left, right)),
                                           0.)

                if left.value < right.value:
                    a, b = left.value, right.value
                else:
                    a, b = right.value, left.value

                if ic_mica > 0.:
                    previous = data.get_similarity(a, b)
                    data.set_similarity(a, b, max(ic_mica, previous))
                    count += 1
                if count % 5_000 == 0 and count != 0:
                    logger.info(f'Processed {count:,d} term pairs')

    return data
