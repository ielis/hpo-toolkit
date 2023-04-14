import abc
import enum
import logging
import typing

logger = logging.getLogger("hpotk.ontology.io.obographs")


class NodeType(enum.Enum):
    CLASS = 1
    INDIVIDUAL = 2
    PROPERTY = 3


def create_property_value(cls, data: typing.Dict):
    if cls == PropertyValue:
        return PropertyValue(pred=get_attr_or_none(data, 'pred'),
                             val=get_attr_or_none(data, 'val'),
                             xrefs=data['xrefs'] if 'xrefs' in data else [],
                             meta=create_meta(data['meta']) if 'meta' in data else None)
    elif cls == DefinitionPropertyValue:
        return DefinitionPropertyValue(pred=get_attr_or_none(data, 'pred'),
                                       val=get_attr_or_none(data, 'val'),
                                       xrefs=data['xrefs'] if 'xrefs' in data else [],
                                       meta=create_meta(data['meta']) if 'meta' in data else None)
    elif cls == BasicPropertyValue:
        return BasicPropertyValue(pred=get_attr_or_none(data, 'pred'),
                                  val=get_attr_or_none(data, 'val'),
                                  xrefs=data['xrefs'] if 'xrefs' in data else [],
                                  meta=create_meta(data['meta']) if 'meta' in data else None)
    elif cls == XrefPropertyValue:
        return XrefPropertyValue(lbl=get_attr_or_none(data, 'lbl'),
                                 pred=get_attr_or_none(data, 'pred'),
                                 val=get_attr_or_none(data, 'val'),
                                 xrefs=data['xrefs'] if 'xrefs' in data else [],
                                 meta=create_meta(data['meta']) if 'meta' in data else None)
    elif cls == SynonymPropertyValue:
        return SynonymPropertyValue(synonym_type=get_attr_or_none(data, 'synonymType'),
                                    pred=get_attr_or_none(data, 'pred'),
                                    val=get_attr_or_none(data, 'val'),
                                    xrefs=data['xrefs'] if 'xrefs' in data else [],
                                    meta=create_meta(data['meta']) if 'meta' in data else None)
    else:
        return None


class PropertyValue:

    def __init__(self, pred: typing.Optional[str],
                 val: typing.Optional[str],
                 xrefs: typing.Sequence[str],
                 meta):
        self._pred = pred
        self._val = val
        self._xrefs = xrefs
        self._meta = meta

    @property
    def pred(self) -> typing.Optional[str]:
        return self._pred

    @property
    def val(self) -> typing.Optional[str]:
        return self._val

    @property
    def xrefs(self) -> typing.Sequence[str]:
        return self._xrefs

    @property
    def meta(self):
        return self._meta

    def __str__(self):
        return f'PropertyValue(pred={self.pred}, val={self.val}, xrefs={self.xrefs}, meta={self.meta})'

    def __repr__(self):
        return str(self)


class DefinitionPropertyValue(PropertyValue):

    def __str__(self):
        return f'DefinitionPropertyValue(pred={self.pred}, val={self.val}, xrefs={self.xrefs}, meta={self.meta})'

    def __repr__(self):
        return str(self)


class BasicPropertyValue(PropertyValue):

    def __str__(self):
        return f'BasicPropertyValue(pred={self.pred}, val={self.val}, xrefs={self.xrefs}, meta={self.meta})'

    def __repr__(self):
        return str(self)


class XrefPropertyValue(PropertyValue):

    def __init__(self, lbl: typing.Optional[str],
                 pred: typing.Optional[str],
                 val: typing.Optional[str],
                 xrefs: typing.Sequence[str],
                 meta):
        super().__init__(pred, val, xrefs, meta)
        self._lbl = lbl

    @property
    def lbl(self) -> typing.Optional[str]:
        return self._lbl

    def __str__(self):
        return f'XrefPropertyValue(lbl={self.lbl}, pred={self.pred}, val={self.val}, xrefs={self.xrefs}, meta={self.meta})'

    def __repr__(self):
        return str(self)


class SynonymPropertyValue(PropertyValue):

    def __init__(self, synonym_type: typing.Optional[str],
                 pred: typing.Optional[str],
                 val: typing.Optional[str],
                 xrefs: typing.Sequence[str],
                 meta):
        super().__init__(pred, val, xrefs, meta)
        self._synonym_type = synonym_type

    @property
    def synonym_type(self) -> typing.Optional[str]:
        return self._synonym_type

    def __str__(self):
        return f'SynonymPropertyValue(' \
               f'synonym_type={self.synonym_type},' \
               f' pred={self.pred},' \
               f' val={self.val},' \
               f' xrefs={self.xrefs},' \
               f' meta={self.meta})'

    def __repr__(self):
        return str(self)


class Meta:

    def __init__(self, definition: typing.Optional[DefinitionPropertyValue],
                 synonyms: typing.Sequence[SynonymPropertyValue],
                 comments: typing.Sequence[str],
                 basic_property_values: typing.Sequence[BasicPropertyValue],
                 xrefs: typing.Sequence[XrefPropertyValue],
                 is_deprecated: bool):
        self._definition = definition
        self._synonyms = synonyms
        self._comments = comments
        self._property_values = basic_property_values
        self._xrefs = xrefs
        self._is_deprecated = is_deprecated

    @property
    def definition(self) -> typing.Optional[DefinitionPropertyValue]:
        return self._definition

    @property
    def synonyms(self) -> typing.Sequence[SynonymPropertyValue]:
        return self._synonyms

    @property
    def comments(self) -> typing.Sequence[str]:
        return self._comments

    @property
    def basic_property_values(self) -> typing.Sequence[BasicPropertyValue]:
        return self._property_values

    @property
    def xrefs(self) -> typing.Sequence[XrefPropertyValue]:
        return self._xrefs

    @property
    def is_deprecated(self) -> bool:
        return self._is_deprecated

    def __str__(self):
        return f'Meta(definition={self.definition},' \
               f' synonyms={self.synonyms},' \
               f' comments={self.comments},' \
               f' basic_property_values={self.basic_property_values},' \
               f' xrefs={self.xrefs},' \
               f' is_deprecated={self.is_deprecated})'

    def __repr__(self):
        return str(self)


class NodeOrEdge(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def meta(self) -> typing.Optional[Meta]:
        pass


class Node(NodeOrEdge):

    def __init__(self, id: str,
                 lbl: typing.Optional[str],
                 node_type: NodeType,
                 meta: typing.Optional[Meta]):
        self._id = id
        self._lbl = lbl
        self._type = node_type
        self._meta = meta

    @property
    def id(self) -> str:
        return self._id

    @property
    def lbl(self) -> typing.Optional[str]:
        return self._lbl

    @property
    def type(self) -> NodeType:
        return self._type

    @property
    def meta(self) -> typing.Optional[Meta]:
        return self._meta

    def __str__(self):
        return f'Node(id={self.id}, lbl={self.lbl}, type={self.type} meta={self.meta})'

    def __repr__(self):
        return str(self)


class Edge(NodeOrEdge):

    def __init__(self, sub: str,
                 pred: str,
                 obj: str,
                 meta: typing.Optional[Meta]):
        self._sub = sub
        self._pred = pred
        self._obj = obj
        self._meta = meta

    @property
    def sub(self) -> str:
        return self._sub

    @property
    def pred(self) -> str:
        return self._pred

    @property
    def obj(self) -> str:
        return self._obj

    @property
    def meta(self) -> typing.Optional[Meta]:
        return self._meta

    def __str__(self):
        return f'Edge(sub={self.sub}, pred={self.pred}, obj={self.obj}, meta={self.meta})'

    def __repr__(self):
        return str(self)


def get_attr_or_none(data: dict, key: str):
    return data[key] if key in data else None


def create_meta(data) -> typing.Optional[Meta]:
    definition = create_property_value(DefinitionPropertyValue, data['definition']) if 'definition' in data else None
    comments = data['comments'] if 'comments' in data else []
    basic_property_values = [create_property_value(BasicPropertyValue, d) for d in
                             data['basicPropertyValues']] if 'basicPropertyValues' in data else []
    synonyms = [create_property_value(SynonymPropertyValue, x) for x in data['synonyms']] if 'synonyms' in data else []
    xrefs = [create_property_value(XrefPropertyValue, x) for x in data['xrefs']] if 'xrefs' in data else []
    is_deprecated = 'deprecated' in data

    return Meta(definition, synonyms, comments, basic_property_values, xrefs, is_deprecated)


def create_node(data) -> typing.Optional[Node]:
    identifier = data['id']
    lbl = data['lbl'] if 'lbl' in data else None

    if 'type' not in data:
        logger.debug(f'Missing node type in {data}')
        # We cannot create a Node with no type.
        return None

    nt = data['type']
    try:
        node_type = NodeType[nt]
    except KeyError:
        logger.debug(f'Unknown node type {nt}. Supported: {list(NodeType)}')
        return None

    if 'meta' in data:
        meta = create_meta(data['meta'])
    else:
        meta = None

    return Node(identifier, lbl, node_type, meta)


def create_edge(data) -> Edge:
    if not all([key in data for key in ['sub', 'pred', 'obj']]):
        raise ValueError(f'Missing required property for an edge {data}')
    meta = create_meta(data['meta']) if 'meta' in data else None
    return Edge(data['sub'], data['pred'], data['obj'], meta)
