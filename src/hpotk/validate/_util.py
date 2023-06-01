import typing

from hpotk.model import TermId, Identified, ObservableFeature


# #################################################################################################################### #
# Non-public utilities
# #################################################################################################################### #


class SimpleFeature(Identified, ObservableFeature):

    def __init__(self, identifier: TermId, status: bool):
        self._id = identifier
        self._status = status

    @property
    def identifier(self) -> TermId:
        return self._id

    @identifier.setter
    def identifier(self, value: TermId):
        self._id = value

    @property
    def is_present(self) -> bool:
        return self._status


def map_to_stateful_feature(feature: typing.Union[Identified, TermId]) -> SimpleFeature:
    if isinstance(feature, Identified):
        term_id = feature.identifier
        if hasattr(feature, 'is_present'):
            attr = feature.is_present
            if hasattr(attr, '__call__'):
                status = attr()
                if not isinstance(status, bool):
                    raise ValueError(f'Feature {feature} has a callable `is_present` but it does not produce a `bool` '
                                     f'but {type(status)}')
            elif isinstance(attr, bool):
                status = attr
            else:
                raise ValueError(f'Feature {feature} has `is_present` attribute but the attribute is not a callable '
                                 f'or a `bool`')
        else:
            status = True  # we assume the feature was observed
    elif isinstance(feature, TermId):
        term_id = feature
        status = True  # we assume the feature was observed
    else:
        raise ValueError(f'Feature {feature} must implement `TermId` or `Identified`')

    return SimpleFeature(term_id, status)
